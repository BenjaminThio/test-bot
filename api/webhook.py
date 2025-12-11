from telegram import Update
from telegram.ext import Application, CommandHandler
import os

TOKEN = os.environ["BOT_TOKEN"]

app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("Hello from Vercel!")

app.add_handler(CommandHandler("start", start))


# Vercel handler
async def handler(request):
    if request.method == "POST":
        body = await request.json()
        update = Update.de_json(body, app.bot)
        await app.process_update(update)
        return {"statusCode": 200}
    else:
        return {"statusCode": 200, "body": "Bot running."}
