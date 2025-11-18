import axios from "axios";
import { getBanglaDate, getEnglishDate } from "./date.js";

const weekdayBn = {
  Sunday: "রবিবার",
  Monday: "সোমবার",
  Tuesday: "মঙ্গলবার",
  Wednesday: "বুধবার",
  Thursday: "বৃহস্পতিবার",
  Friday: "শুক্রবার",
  Saturday: "শনিবার"
};

const bn = n =>
  String(n).replace(/[0-9]/g, d =>
    "০১২৩৪৫৬৭৮৯"[d]
  );

export async function getPrayerAndHijri(tomorrow = false) {
  const dateParam = tomorrow ? 1 : 0;

  const res = await axios.get(
    "https://api.aladhan.com/v1/timingsByCity",
    {
      params: {
        city: "Dhaka",
        country: "Bangladesh",
        method: 2,
        tune: "0"
      }
    }
  );

  return res.data.data;
}

export async function composeMessage(tomorrow = false) {
  const eng = getEnglishDate("Asia/Dhaka", tomorrow);
  const ban = getBanglaDate("Asia/Dhaka", tomorrow);
  const api = await getPrayerAndHijri(tomorrow);

  const h = api.date.hijri;
  const t = api.timings;

  return `
আসসালামু আলাইকুম ওয়ারাহমাতুল্লাহ্।
🟧আজ ${weekdayBn[eng.weekday]}।
🟩${bn(eng.day)} ${eng.month} ${bn(eng.year)} খ্রিষ্টাব্দ।
🟦${bn(ban.day)} ${ban.month} ${bn(ban.year)} বঙ্গাব্দ।
🟪${bn(h.day)} ${h.month.en} ${bn(h.year)} হিজরী।
🌅ঋতু- ${ban.season}।
⬛ফজর- ${bn(t.Fajr)} মিনিট।
🟨যোহর- ${bn(t.Dhuhr)} মিনিট।
🟫আসর- ${bn(t.Asr)} মিনিট।
🔲মাগরিব- ${bn(t.Maghrib)} মিনিট।
⬜ইশা- ${bn(t.Isha)} মিনিট।
🌄সূর্যোদয়- ${bn(t.Sunrise)} মিনিট এবং
⏺সূর্যাস্ত- ${bn(t.Sunset)} মিনিট (ঢাকা)।
  `.trim();
}
