import os
import json
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, APP_URL

bot = Bot(token=TELEGRAM_BOT_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

DATA_FILE = "store.json"
CHECK_INTERVAL = 60  # seconds

users = {}  # user_id: {username, cookie}

# ------------------- Helpers --------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ------------------- Commands ------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Pinterest Bot!\nUse /login to begin.\nThen use /setcookie and /setuser.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    login_url = f"{APP_URL}/login?uid={user_id}"
    await update.message.reply_text(f"🔐 Click to login:\n{login_url}")

async def setcookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setcookie <_pinterest_sess_cookie>")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {}
    data[user_id]["cookie"] = context.args[0]
    save_data(data)

    await update.message.reply_text("✅ Cookie saved successfully!")

async def setuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setuser <pinterest_username>")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {}
    data[user_id]["username"] = context.args[0]
    data[user_id]["last_pin"] = ""
    save_data(data)

    await update.message.reply_text(f"✅ Now watching: {context.args[0]}\nUse /startwatch to begin.")

async def startwatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data or "username" not in data[user_id] or "cookie" not in data[user_id]:
        await update.message.reply_text("⚠️ Please complete /setuser and /setcookie first.")
        return

    await update.message.reply_text("⏱️ Started watching your saved pins...")

    async def monitor():
        from scraper import get_latest_pin  # import here to avoid error if not implemented

        while True:
            user_data = load_data().get(user_id, {})
            cookie = user_data.get("cookie")
            username = user_data.get("username")
            last_pin = user_data.get("last_pin", "")

            new_pin = get_latest_pin(username, cookie)
            if new_pin and new_pin["link"] != last_pin:
                await bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=new_pin["image"],
                    caption=f"📌 New Saved Pin:\n{new_pin['title']}\n🔗 {new_pin['link']}"
                )
                user_data["last_pin"] = new_pin["link"]
                all_data = load_data()
                all_data[user_id] = user_data
                save_data(all_data)

            await asyncio.sleep(CHECK_INTERVAL)

    app.create_task(monitor())

# ------------------- Handlers ------------------------

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("setcookie", setcookie))
app.add_handler(CommandHandler("setuser", setuser))
app.add_handler(CommandHandler("startwatch", startwatch))

if __name__ == "__main__":
    app.run_polling()
