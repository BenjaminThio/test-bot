import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = FastAPI()

# Initialize Bot Token
TOKEN = os.environ.get("TOKEN")

# --- Define your Bot Logic here ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="I am alive and running on Vercel (v20)!"
    )

# --- Webhook Handler ---
@app.post("/webhook")
async def webhook(request: Request):
    if not TOKEN:
        return {"error": "TOKEN environment variable is missing"}

    # 1. Decode the update from Telegram
    data = await request.json()
    
    # 2. Build the Application (Serverless-safe mode)
    # We build a fresh app instance per request to avoid "frozen" state issues
    application = ApplicationBuilder().token(TOKEN).build()

    # 3. Register your handlers
    application.add_handler(CommandHandler('start', start))

    # 4. Process the update
    # The 'await' here is the magic that fixes the "Silent Bot" issue.
    # It forces Vercel to keep the server running until the bot replies.
    async with application:
        await application.process_update(
            Update.de_json(data, application.bot)
        )

    return {"message": "ok"}

@app.get("/")
def index():
    return {"message": "Bot is running"}