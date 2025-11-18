import os
import json
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from bot_utils import build_message
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

dispatcher = Dispatcher(bot, None, workers=0)

# /today command handler
def today_cmd(update: Update, context: CallbackContext):
    from datetime import datetime
    import pytz
    tz = pytz.timezone("Asia/Dhaka")
    today = datetime.now(tz).date()

    update.effective_chat
    msg = build_message(today)
    update.message.reply_text(msg)

dispatcher.add_handler(CommandHandler("today", today_cmd))


# Vercel handler
def handler(request):
    try:
        body = request.get_json()

        if body:
            update = Update.de_json(body, bot)
            dispatcher.process_update(update)

        return {"statusCode": 200, "body": "OK"}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
