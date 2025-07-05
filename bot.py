import os
import json
import asyncio
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN
from scraper import get_latest_pin, validate_cookie, validate_username

bot = Bot(token=TELEGRAM_BOT_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

DATA_FILE = "store.json"
CHECK_INTERVAL = 600  # 10 minutes

# ------------------- Helpers --------------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def now_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ------------------- Commands ------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Pinterest Watch Bot!\nUse /setcookie and /setuser to begin.")

async def setcookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setcookie <_pinterest_sess_cookie>")
        return

    cookie = context.args[0]
    if not validate_cookie(cookie):
        await update.message.reply_text("❌ Invalid cookie. Please make sure it's the correct _pinterest_sess.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {}
    data[user_id]["cookie"] = cookie
    save_data(data)

    await update.message.reply_text("✅ Cookie saved and validated successfully!")

async def setuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setuser <pinterest_username>")
        return

    username = context.args[0]
    data = load_data()
    cookie = data.get(user_id, {}).get("cookie")

    if not cookie:
        await update.message.reply_text("⚠️ Please set cookie first using /setcookie")
        return

    if not validate_username(username, cookie):
        await update.message.reply_text("❌ Invalid Pinterest username or no saved pins found.")
        return

    if user_id not in data:
        data[user_id] = {}
    data[user_id]["username"] = username
    data[user_id]["last_pin"] = ""
    data[user_id]["last_time"] = ""
    save_data(data)

    await update.message.reply_text(f"✅ Watching Pinterest account: {username}\nUse /startwatch to begin.")

async def startwatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    user_data = data.get(user_id, {})

    if "username" not in user_data or "cookie" not in user_data:
        await update.message.reply_text("⚠️ Use /setcookie and /setuser first.")
        return

    username = user_data["username"]
    cookie = user_data["cookie"]
    last_pin = user_data.get("last_pin", "")
    last_time = user_data.get("last_time", "")

    await update.message.reply_text("⏱️ Watching saved pins. You'll be notified when a new one is added.")

    async def monitor():
        while True:
            latest = get_latest_pin(username, cookie)
            full_data = load_data()
            user_data = full_data.get(user_id, {})

            if latest and latest["link"] != user_data.get("last_pin", ""):
                await bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=latest["image"],
                    caption=f"📌 New Saved Pin:\n{latest['title']}\n🔗 {latest['link']}"
                )
                user_data["last_pin"] = latest["link"]
                user_data["last_time"] = now_time_str()
            else:
                await bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"🕒 No new pins in last 10 mins.\nLast saved: {user_data.get('last_time', 'N/A')}"
                )

            full_data[user_id] = user_data
            save_data(full_data)
            await asyncio.sleep(CHECK_INTERVAL)

    app.create_task(monitor())

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data().get(user_id, {})
    msg = f"""📊 Your Watch Status:
👤 Username: {data.get('username', '❌ Not set')}
🔐 Cookie: {"✅ Set" if data.get("cookie") else "❌ Not set"}
📌 Last Pin: {data.get('last_pin', 'N/A')}
🕒 Last Saved Time: {data.get('last_time', 'N/A')}
⏱ Interval: 10 minutes
"""
    await update.message.reply_text(msg)

# ------------------- Handlers ------------------------

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setcookie", setcookie))
app.add_handler(CommandHandler("setuser", setuser))
app.add_handler(CommandHandler("startwatch", startwatch))
app.add_handler(CommandHandler("status", status))

if __name__ == "__main__":
    app.run_polling()
