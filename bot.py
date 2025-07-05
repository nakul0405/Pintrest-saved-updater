import os
import json
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from scraper import get_latest_pin  # You'll need to define this function
from config import TELEGRAM_BOT_TOKEN, ADMIN_CHAT_ID

DATA_FILE = "store.json"
CHECK_INTERVAL = 60  # seconds
APP_URL = "https://your-app-name.up.railway.app"  # <-- change this!

bot = Bot(token=TELEGRAM_BOT_TOKEN)
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

watching_username = None
sp_dc_cookie = None

# ------------------- Data Storage --------------------

def load_last_pin():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_pin(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ------------------- Commands ------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Pinterest Watch Bot!\nUse /login to log in and /setuser <username> to begin.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔐 Click to log in to Pinterest:\n{APP_URL}/login"
    )

async def setcookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sp_dc_cookie
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setcookie <sp_dc_cookie>")
        return
    sp_dc_cookie = context.args[0]
    await update.message.reply_text("✅ sp_dc cookie set successfully!")

async def setuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global watching_username
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setuser <pinterest_username>")
        return
    watching_username = context.args[0]
    save_last_pin({watching_username: ""})
    await update.message.reply_text(f"✅ Now watching: {watching_username}\nUse /startwatch to begin.")

async def startwatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not watching_username:
        await update.message.reply_text("⚠️ Use /setuser first.")
        return
    if not sp_dc_cookie:
        await update.message.reply_text("⚠️ Login required! Use /login and complete Pinterest login first.")
        return

    await update.message.reply_text("⏱️ Started watching Pinterest saved pins...")

    async def monitor():
        while True:
            last_pin_data = load_last_pin()
            last_pin = last_pin_data.get(watching_username, "")
            new_pin = get_latest_pin(watching_username, sp_dc_cookie)  # ← scraper.py must support cookie
            if new_pin and new_pin["link"] != last_pin:
                await bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=new_pin["image"],
                    caption=f"📌 New Pin Saved:\n{new_pin['title']}\n🔗 {new_pin['link']}"
                )
                last_pin_data[watching_username] = new_pin["link"]
                save_last_pin(last_pin_data)
            await asyncio.sleep(CHECK_INTERVAL)

    app.create_task(monitor())

# ------------------- Register Handlers ------------------------

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("setcookie", setcookie))
app.add_handler(CommandHandler("setuser", setuser))
app.add_handler(CommandHandler("startwatch", startwatch))

if __name__ == "__main__":
    app.run_polling()
