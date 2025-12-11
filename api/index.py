# api/index.py file content

import os
import logging
from fastapi import FastAPI, Request, status
from mangum import Mangum
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    """Handles the /start command."""
    await update.message.reply_text(
        f"Hello, {update.effective_user.first_name}! I'm your Vercel-hosted Python bot."
    )

async def echo(update: Update, context):
    """Echoes the user's text message."""
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN environment variable is not set!")
    pass

application = (
    Application.builder()
    .token(TOKEN)
    .build()
)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app = FastAPI()

@app.get("/")
def home():
    """Simple endpoint to confirm the function is active."""
    return {"status": "Vercel bot is running, awaiting webhook POSTs at /api"}

@app.post("/api")
async def telegram_webhook(request: Request):
    """Receives and processes the Telegram webhook POST request."""
    try:
        body = await request.json()
        logger.info("Received update: %s", body)
        update = Update.de_json(body, application.bot)

        await application.process_update(update)

        return {"status": "ok"}, status.HTTP_200_OK
    
    except Exception as e:
        logger.error("Error processing update: %s", e)
        return {"status": "error", "message": str(e)}, status.HTTP_200_OK

handler = Mangum(app)