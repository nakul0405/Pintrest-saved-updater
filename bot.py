print("🚀 Bot started")
print("TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))

from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler
import asyncio
from scraper import get_latest_pin
import json
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHECK_INTERVAL = 60  # seconds
DATA_FILE = "store.json"

bot = Bot(token=TOKEN)
app = ApplicationBuilder().token(TOKEN).build()
watching_username = None

def load_last_pin():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_pin(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context):
    await update.message.reply_text("👋 Welcome to Pinterest Watch Bot!\nUse /setuser <username> to begin.")

async def setuser(update: Update, context):
    global watching_username
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setuser <pinterest_username>")
        return
    watching_username = context.args[0]
    save_last_pin({watching_username: ""})
    await update.message.reply_text(f"✅ Now watching: {watching_username}\nUse /startwatch to begin scraping.")

async def startwatch(update: Update, context):
    if not watching_username:
        await update.message.reply_text("⚠️ Use /setuser first.")
        return
    await update.message.reply_text("⏱️ Started watching Pinterest pins...")

    async def monitor():
        while True:
            last_pin_data = load_last_pin()
            last_pin = last_pin_data.get(watching_username, "")
            new_pin = get_latest_pin(watching_username)
            if new_pin and new_pin["link"] != last_pin:
                await bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=new_pin["image"],
                    caption=f"📌 New Pin:\n{new_pin['title']}\n🔗 {new_pin['link']}"
                )
                last_pin_data[watching_username] = new_pin["link"]
                save_last_pin(last_pin_data)
            await asyncio.sleep(CHECK_INTERVAL)

    app.create_task(monitor())

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setuser", setuser))
app.add_handler(CommandHandler("startwatch", startwatch))

if __name__ == "__main__":
    app.run_polling()
