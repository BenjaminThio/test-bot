# api/index.py file content

import os
import logging
from fastapi import FastAPI, Request, status
from mangum import Mangum
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Check the Token ---
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    # Log an explicit error if the token is missing
    logger.error("FATAL ERROR: BOT_TOKEN is missing or None.")
    # You might want to return an error response immediately here
    # to avoid the crash, but let's see the logs first.
else:
    # Log the successful retrieval (masking the secret for security)
    logger.info("BOT_TOKEN successfully retrieved. Length: %d", len(TOKEN))
    logger.info("First 5 chars of token: %s*****", TOKEN[:5])


# --- Build the Application (Global Scope) ---
# If TOKEN is None, this line will likely cause the TypeError: issubclass() crash
application = (
    Application.builder()
    .token(TOKEN)
    .build()
)

async def start(update: Update, context):
    """Handles the /start command."""
    await update.message.reply_text(
        f"Hello, {update.effective_user.first_name}! I'm your Vercel-hosted Python bot."
    )

async def echo(update: Update, context):
    """Echoes the user's text message."""
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

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