import moment from "moment-timezone";
import BanglaDate from "bangla-date";

export function getBanglaDate(tz = "Asia/Dhaka", tomorrow = false) {
  let m = moment().tz(tz);
  if (tomorrow) m.add(1, "day");

  const bd = new BanglaDate(m.toDate());

  return {
    day: bd.getDate(),
    month: bd.getMonth(),
    year: bd.getYear(),
    season: bd.getSeason()
  };
}

export function getEnglishDate(tz = "Asia/Dhaka", tomorrow = false) {
  let m = moment().tz(tz);
  if (tomorrow) m.add(1, "day");

  return {
    weekday: m.format("dddd"),
    day: m.format("D"),
    month: m.format("MMMM"),
    year: m.format("YYYY")
  };
}
