import os
import json
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler
from scraper import get_latest_pin

print("🚀 Bot started")
print("TOKEN:", "Loaded" if os.getenv("TELEGRAM_BOT_TOKEN") else "❌ Missing!")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHECK_INTERVAL = 60  # in seconds
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
    await update.message.reply_text(f"✅ Now watching: {watching_username}\nUse /startwatch to begin tracking pins.")

async def startwatch(update: Update, context):
    if not watching_username:
        await update.message.reply_text("⚠️ Please set a username first using /setuser")
        return

    await update.message.reply_text(f"🔎 Started watching `{watching_username}` pins...\n⏱️ Checking every {CHECK_INTERVAL} seconds.", parse_mode="Markdown")

    async def monitor():
        while True:
            try:
                last_data = load_last_pin()
                last_pin_link = last_data.get(watching_username, "")
                new_pin = get_latest_pin(watching_username)

                if new_pin and new_pin["link"] != last_pin_link:
                    await bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=new_pin["image"],
                        caption=f"📌 New Pin Detected!\n🔗 {new_pin['link']}"
                    )
                    last_data[watching_username] = new_pin["link"]
                    save_last_pin(last_data)
                else:
                    print("📭 No new pin.")
            except Exception as e:
                print("❌ Monitor error:", e)

            await asyncio.sleep(CHECK_INTERVAL)

    app.create_task(monitor())

# Telegram Command Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setuser", setuser))
app.add_handler(CommandHandler("startwatch", startwatch))

# Run the bot
if __name__ == "__main__":
    app.run_polling()
