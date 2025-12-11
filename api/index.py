import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Initialize FastAPI
app = FastAPI()

# Get Token
TOKEN = os.environ.get("TOKEN")

# 1. Define the handler function (Must be async now!)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="I'm a bot, please talk to me!"
    )

# 2. Build the Application (Replaces Dispatcher)
# We build it globally so we don't rebuild it on every request if Vercel keeps the instance warm
if TOKEN:
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Register handlers
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

@app.post("/webhook")
async def webhook(request: Request):
    """
    Handle Telegram Webhook
    """
    if not TOKEN:
        return {"error": "Token not found"}

    # 1. Load the JSON data
    data = await request.json()

    # 2. Decode the update
    # In v20, we don't need the bot instance here, just the data
    update = Update.de_json(data, application.bot)

    # 3. Process the update
    # 'await' ensures the bot waits for the message to be sent before finishing
    await application.initialize()
    await application.process_update(update)

    return {"message": "ok"}

@app.get("/")
def index():
    return {"message": "Bot is running!"}