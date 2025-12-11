import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get Token
TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="I am running on Render! 🚀"
    )

if __name__ == '__main__':
    # Build the app
    application = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    # Run the bot (Polling mode)
    # This runs forever, which is allowed on Render!
    print("Bot is starting...")
    application.run_polling()