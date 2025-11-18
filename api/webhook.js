import axios from "axios";
import { composeMessage } from "../utils/message.js";

export default async function handler(req, res) {
  try {
    const update = req.body;

    if (update.message) {
      const chatId = update.message.chat.id;
      const text = update.message.text;

      if (text === "/today") {
        const msg = await composeMessage(false);
        await send(chatId, msg);
      }

      if (text === "/tomorrow") {
        const msg = await composeMessage(true);
        await send(chatId, msg);
      }
    }

    res.status(200).send("OK");
  } catch (e) {
    console.log(e);
    res.status(200).send("OK");
  }
}

async function send(chat_id, text) {
  return axios.post(
    `https://api.telegram.org/bot${process.env.TOKEN}/sendMessage`,
    { chat_id, text }
  );
}
