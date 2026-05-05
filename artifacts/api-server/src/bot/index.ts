import TelegramBot from "node-telegram-bot-api";
import { logger } from "../lib/logger.js";
import { registerHandlers } from "./handlers.js";

export function startBot(): TelegramBot | null {
  const token = process.env["TELEGRAM_BOT_TOKEN"];

  if (!token) {
    logger.warn("TELEGRAM_BOT_TOKEN not set — Telegram bot will not start");
    return null;
  }

  const bot = new TelegramBot(token, { polling: true });

  registerHandlers(bot);

  bot.getMe().then((me) => {
    logger.info({ username: me.username }, "Telegram bot started");
  }).catch((err) => {
    logger.error({ err }, "Failed to get bot info");
  });

  return bot;
}
