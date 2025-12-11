import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler

# Initialize FastAPI
app = FastAPI()

# Get Token safely
TOKEN = os.environ.get("BOT_TOKEN")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def register_handlers(dispatcher):
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

@app.post("/webhook")
async def webhook(request: Request):
    """
    Handle Telegram Webhook
    """
    # 1. Load the JSON data directly (safer than using a strict Pydantic model)
    data = await request.json()

    # 2. Initialize Bot and Dispatcher
    bot = Bot(token=TOKEN)
    
    # 3. decode the update
    update = Update.de_json(data, bot)

    # 4. CRITICAL FIX: workers=0
    # This forces the bot to process the message IMMEDIATELY in the main thread.
    # If you use workers=4, the Vercel function will close before the bot replies.
    dispatcher = Dispatcher(bot, None, workers=0)
    
    # 5. Register handlers
    register_handlers(dispatcher)

    # 6. Process the update (Blocking)
    dispatcher.process_update(update)

    return {"message": "ok"}

@app.get("/")
def index():
    return {"message": "Hello World"}