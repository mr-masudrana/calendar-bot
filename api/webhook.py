import json
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from bot_utils import build_message
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# /today command
def today(update: Update, context: CallbackContext):
    from datetime import datetime
    import pytz
    tz = pytz.timezone("Asia/Dhaka")
    msg = build_message(datetime.now(tz).date())
    update.message.reply_text(msg)

dispatcher.add_handler(CommandHandler("today", today))


# Vercel Python Handler (VERY IMPORTANT)
def handler(request):
    try:
        body = request.get_json()

        if body:
            update = Update.de_json(body, bot)
            dispatcher.process_update(update)

        return {
            "statusCode": 200,
            "body": "OK"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
