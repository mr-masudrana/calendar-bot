import requests
import pytz
from datetime import date

def en_to_bn(n):
    mapping = {"0":"০","1":"১","2":"২","3":"৩","4":"৪",
               "5":"৫","6":"৬","7":"৭","8":"৮","9":"৯"}
    return "".join(mapping.get(c, c) for c in str(n))


def gregorian_to_bangla_date(g_date):
    byear = g_date.year - 593
    months = [
        ("বৈশাখ",14,4),("জ্যৈষ্ঠ",15,5),("আষাঢ়",15,6),("শ্রাবণ",16,7),
        ("ভাদ্র",17,8),("আশ্বিন",17,9),("কার্তিক",18,10),("অগ্রহায়ণ",17,11),
        ("পৌষ",16,12),("মাঘ",15,1),("ফাল্গুন",13,2),("চৈত্র",15,3)
    ]
    
    for name,start_day,start_m in months:
        if g_date.month == start_m and g_date.day >= start_day:
            bday = g_date.day - start_day + 1
            return f"{en_to_bn(bday)} {name} {en_to_bn(byear)} বঙ্গাব্দ", name
    
    return f"{en_to_bn(g_date.day)} চৈত্র {en_to_bn(byear)} বঙ্গাব্দ", "চৈত্র"


def get_ritu(month_bn):
    ritu = {
        "বৈশাখ":"গ্রীষ্ম","জ্যৈষ্ঠ":"গ্রীষ্ম",
        "আষাঢ়":"বর্ষা","শ্রাবণ":"বর্ষা",
        "ভাদ্র":"শরৎ","আশ্বিন":"শরৎ",
        "কার্তিক":"হেমন্ত","অগ্রহায়ণ":"হেমন্ত",
        "পৌষ":"শীত","মাঘ":"শীত",
        "ফাল্গুন":"বসন্ত","চৈত্র":"বসন্ত"
    }
    return ritu.get(month_bn, "")


def build_message(today: date):
    week_map = {
        "Saturday":"শনিবার","Sunday":"রবিবার","Monday":"সোমবার",
        "Tuesday":"মঙ্গলবার","Wednesday":"বুধবার",
        "Thursday":"বৃহস্পতিবার","Friday":"শুক্রবার"
    }

    weekday = week_map[today.strftime("%A")]
    eng_date = today.strftime("%d %B %Y")

    bn_date, bn_month = gregorian_to_bangla_date(today)
    ritu = get_ritu(bn_month)

    # API
    url = f"https://api.aladhan.com/v1/timingsByCity/{today.strftime('%d-%m-%Y')}"
    params = {"city": "Dhaka", "country": "Bangladesh", "method": 1}

    try:
        r = requests.get(url, params=params)
        data = r.json()
        timings = data["data"]["timings"]
        hijri = data["data"]["date"]["hijri"]
        hijri_text = f"{hijri['day']} {hijri['month']['ar']} {hijri['year']}"
    except:
        timings = {}
        hijri_text = "N/A"

    def T(k):
        return timings.get(k, "N/A")

    msg = f"""
আসসালামু আলাইকুম ওয়ারাহমাতুল্লাহ্।
🟧আজ {weekday}
🟩{eng_date}
🟦{bn_date}
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
