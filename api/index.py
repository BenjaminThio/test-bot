# api/index.py content (using Flask)

import os
import json
import logging
# --- FLASK Imports ---
from flask import Flask, request, jsonify 
# ---------------------
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Check the Token ---
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    logger.error("FATAL ERROR: BOT_TOKEN is missing or None.")

# --- Build the Application (Global Scope) ---
application = (
    Application.builder()
    .token(TOKEN)
    .build()
)

async def start(update: Update, context):
    """Handles the /start command."""
    await update.message.reply_text(
        f"Hello, {update.effective_user.first_name}! I'm your Vercel-hosted Flask bot."
    )

async def echo(update: Update, context):
    """Echoes the user's text message."""
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# --- Define the Flask App to handle the Webhook ---
# Vercel will automatically recognize the 'app' variable as the entry point
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def telegram_webhook():
    """Receives and processes the Telegram webhook POST request."""
    if request.method == "POST":
        try:
            # Flask's way to get the JSON body
            body = request.get_json()
            logger.info("Received update via Flask: %s", body)

            # Create and process the Telegram Update object
            update = Update.de_json(body, application.bot)
            
            # NOTE: We use application.process_update() directly here 
            # (which runs the handlers asynchronously inside the worker)
            application.process_update(update) 

            # Telegram expects an immediate 200 response
            return jsonify({"status": "ok"}), 200
        
        except Exception as e:
            logger.error("Error processing update: %s", e)
            # IMPORTANT: Still return 200 to prevent Telegram from retrying
            return jsonify({"status": "error", "message": str(e)}), 200 
            
    # Default response for GET requests
    return jsonify({"status": "Vercel bot is running, awaiting webhook POSTs at /api"}), 200

# Vercel automatically finds the 'app' object, no 'handler = Mangum(app)' needed.