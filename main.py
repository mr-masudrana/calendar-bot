import os
import logging
from datetime import datetime, date
import requests
import pytz
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

load_dotenv()

# CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_IDS = os.getenv("TARGET_CHAT_IDS", "")
CITY = os.getenv("CITY", "Dhaka")
COUNTRY = os.getenv("COUNTRY", "Bangladesh")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Dhaka")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-domain.com/webhook

CHAT_IDS = [c.strip() for c in TARGET_CHAT_IDS.split(",") if c.strip()]
tz = pytz.timezone(TIMEZONE)

# Telegram
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=2)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# =============== UTILITIES ================

def en_to_bn(n):
    mapping = {"0": "০","1": "১","2": "২","3": "৩","4": "৪",
               "5": "৫","6": "৬","7": "৭","8": "৮","9": "৯"}
    return "".join(mapping.get(ch, ch) for ch in str(n))


def gregorian_to_bangla_date(g_date: date):
    byear = g_date.year - 593

    months = [
        ("বৈশাখ", 14, 4),
        ("জ্যৈষ্ঠ", 15, 5),
        ("আষাঢ়", 15, 6),
        ("শ্রাবণ", 16, 7),
        ("ভাদ্র", 17, 8),
        ("আশ্বিন", 17, 9),
        ("কার্তিক", 18, 10),
        ("অগ্রহায়ণ", 17, 11),
        ("পৌষ", 16, 12),
        ("মাঘ", 15, 1),
        ("ফাল্গুন", 13, 2),
        ("চৈত্র", 15, 3)
    ]

    for name, start_day, start_month in months:
        if g_date.month == start_month and g_date.day >= start_day:
            bday = g_date.day - start_day + 1
            return f"{en_to_bn(bday)} {name} {en_to_bn(byear)} বঙ্গাব্দ", name

    return f"{en_to_bn(g_date.day)} চৈত্র {en_to_bn(byear)} বঙ্গাব্দ", "চৈত্র"


def get_ritu(month_bn):
    ritu_map = {
        "বৈশাখ": "গ্রীষ্ম", "জ্যৈষ্ঠ": "গ্রীষ্ম",
        "আষাঢ়": "বর্ষা", "শ্রাবণ": "বর্ষা",
        "ভাদ্র": "শরৎ", "আশ্বিন": "শরৎ",
        "কার্তিক": "হেমন্ত", "অগ্রহায়ণ": "হেমন্ত",
        "পৌষ": "শীত", "মাঘ": "শীত",
        "ফাল্গুন": "বসন্ত", "চৈত্র": "বসন্ত"
    }
    return ritu_map.get(month_bn, "")


def fetch_prayer_and_hijri(target_date: date):
    url = f"https://api.aladhan.com/v1/timingsByCity/{target_date.strftime('%d-%m-%Y')}"
    params = {"city": CITY, "country": COUNTRY, "method": 1}

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        timings = data["data"]["timings"]
        hijri = data["data"]["date"]["hijri"]
        hijri_text = f"{hijri['day']} {hijri['month']['ar']} {hijri['year']}"
        return timings, hijri_text
    except:
        return None


def build_message(today: date):
    week_map = {
        "Saturday": "শনিবার", "Sunday": "রবিবার", "Monday": "সোমবার",
        "Tuesday": "মঙ্গলবার", "Wednesday": "বুধবার",
        "Thursday": "বৃহস্পতিবার", "Friday": "শুক্রবার"
    }

    weekday = week_map[today.strftime("%A")]
    eng_date = today.strftime("%d %B %Y")

    bn_date, bn_month = gregorian_to_bangla_date(today)
    ritu = get_ritu(bn_month)

    data = fetch_prayer_and_hijri(today)
    if data:
        timings, hijri_text = data
    else:
        timings, hijri_text = {}, "N/A"

    def T(k): return timings.get(k, "N/A")

    msg = f"""আসসালামু আলাইকুম ওয়ারাহমাতুল্লাহ্।
🟧আজ {weekday}।
🟩{eng_date}।
🟦{bn_date}।
🟪হিজরী: {hijri_text}
🌅ঋতু: {ritu}

⬛ফজর: {T('Fajr')}
🟨যোহর: {T('Dhuhr')}
🟫আসর: {T('Asr')}
🔲মাগরিব: {T('Maghrib')}
⬜ইশা: {T('Isha')}

🌄সূর্যোদয়: {T('Sunrise')}
⏺সূর্যাস্ত: {T('Sunset')} (ঢাকা)
"""
    return msg


# =============== COMMANDS =================

def today_cmd(update: Update, context: CallbackContext):
    today = datetime.now(tz).date()
    update.message.reply_text(build_message(today))


dispatcher.add_handler(CommandHandler("today", today_cmd))


# =============== DAILY JOB =================

def send_daily_message():
    today = datetime.now(tz).date()
    msg = build_message(today)
    for cid in CHAT_IDS:
        bot.send_message(cid, msg)


scheduler = BackgroundScheduler(timezone=tz)
scheduler.add_job(send_daily_message, CronTrigger(hour=0, minute=0))
scheduler.start()


# =============== WEBHOOK ENDPOINT ===============

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"ok": True}


# ========== SET WEBHOOK ON SERVER START =========

@app.on_event("startup")
def set_webhook():
    if WEBHOOK_URL:
        full_url = WEBHOOK_URL + "/webhook"
        bot.set_webhook(full_url)
        logger.info("Webhook set to: %s", full_url)
