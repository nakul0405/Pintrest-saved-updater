import os
import json
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler
from scraper import get_latest_pin

print("🚀 Bot started")
print("TOKEN:", "Loaded" if os.getenv("TELEGRAM_BOT_TOKEN") else "❌ Missing!")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHECK_INTERVAL = 60  # seconds
DATA_FILE = "store.json"
COOKIE_FILE = "cookies.json"

bot = Bot(token=TOKEN)
app = ApplicationBuilder().token(TOKEN).build()
watching_username = None

# --- File Helpers ---

def load_last_pin():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_pin(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def save_cookie(sp_dc):
    with open(COOKIE_FILE, "w") as f:
        json.dump({"sp_dc": sp_dc}, f)

# --- Commands ---

async def start(update: Update, context):
    await update.message.reply_text(
        "👋 Welcome to Pinterest Watch Bot!\n"
        "Use /setuser <username> to track someone\n"
        "Use /setcookie <sp_dc_cookie> after logging in Pinterest"
    )

async def setuser(update: Update, context):
    global watching_username
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setuser <pinterest_username>")
        return

    watching_username = context.args[0]
    save_last_pin({watching_username: ""})
    await update.message.reply_text(f"✅ Now watching: {watching_username}")

async def setcookie(update: Update, context):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /setcookie <sp_dc_cookie>")
        return

    cookie_val = context.args[0]
    save_cookie(cookie_val)
    await update.message.reply_text("✅ Cookie saved successfully!")

async def startwatch(update: Update, context):
    if not watching_username:
        await update.message.reply_text("⚠️ Use /setuser first.")
        return

    await update.message.reply_text(f"⏱️ Watching `{watching_username}` pins...", parse_mode="Markdown")

    async def monitor():
        while True:
            try:
                last_data = load_last_pin()
                last_link = last_data.get(watching_username, "")
                new_pin = get_latest_pin(watching_username)

                if new_pin and new_pin["link"] != last_link:
                    await bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=new_pin["image"],
                        caption=f"📌 New Pin:\n🔗 {new_pin['link']}"
                    )
                    last_data[watching_username] = new_pin["link"]
                    save_last_pin(last_data)
                else:
                    print("📭 No new pin.")
            except Exception as e:
                print("❌ Monitor error:", e)

            await asyncio.sleep(CHECK_INTERVAL)

    app.create_task(monitor())

# --- Register Commands ---

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setuser", setuser))
app.add_handler(CommandHandler("startwatch", startwatch))
app.add_handler(CommandHandler("setcookie", setcookie))

if __name__ == "__main__":
    app.run_polling()
