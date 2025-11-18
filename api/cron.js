import axios from "axios";
import { composeMessage } from "../utils/message.js";

export default async function handler(req, res) {
  try {
    const text = await composeMessage(false);

    await axios.post(
      `https://api.telegram.org/bot${process.env.TOKEN}/sendMessage`,
      {
        chat_id: process.env.CHAT_ID,
        text
      }
    );

    res.status(200).json({ ok: true });
  } catch (e) {
    res.status(200).json({ error: e.message });
  }
}
