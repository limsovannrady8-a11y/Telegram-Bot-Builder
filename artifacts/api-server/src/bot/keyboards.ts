import TelegramBot from "node-telegram-bot-api";
import { CALLBACK, SUPPORTED_LANGUAGES } from "./constants.js";

export function mainMenuKeyboard(): TelegramBot.InlineKeyboardMarkup {
  return {
    inline_keyboard: [
      [
        { text: "🗣️ Text-to-Speech", callback_data: CALLBACK.TTS },
        { text: "🎨 Voice Design", callback_data: CALLBACK.VOICE_DESIGN },
      ],
      [
        { text: "🎙️ Voice Clone", callback_data: CALLBACK.VOICE_CLONE },
        { text: "🌍 Languages", callback_data: CALLBACK.LANGUAGES },
      ],
      [
        { text: "ℹ️ About VoxCPM", callback_data: CALLBACK.ABOUT },
        { text: "❓ Help", callback_data: CALLBACK.HELP },
      ],
    ],
  };
}

export function backToMenuKeyboard(): TelegramBot.InlineKeyboardMarkup {
  return {
    inline_keyboard: [
      [
        { text: "❌ Cancel", callback_data: CALLBACK.CANCEL },
        { text: "🏠 Main Menu", callback_data: CALLBACK.MENU },
      ],
    ],
  };
}

export function cancelKeyboard(): TelegramBot.InlineKeyboardMarkup {
  return {
    inline_keyboard: [
      [{ text: "❌ Cancel", callback_data: CALLBACK.CANCEL }],
    ],
  };
}

export function languagesKeyboard(page = 0): TelegramBot.InlineKeyboardMarkup {
  const perPage = 6;
  const start = page * perPage;
  const slice = SUPPORTED_LANGUAGES.slice(start, start + perPage);
  const rows: TelegramBot.InlineKeyboardButton[][] = [];

  for (let i = 0; i < slice.length; i += 2) {
    const row: TelegramBot.InlineKeyboardButton[] = [
      { text: slice[i]!.name, callback_data: `lang_${slice[i]!.code}` },
    ];
    if (slice[i + 1]) {
      row.push({
        text: slice[i + 1]!.name,
        callback_data: `lang_${slice[i + 1]!.code}`,
      });
    }
    rows.push(row);
  }

  const navRow: TelegramBot.InlineKeyboardButton[] = [];
  if (page > 0) {
    navRow.push({ text: "◀️ Prev", callback_data: `${CALLBACK.LANGS_PAGE}_${page - 1}` });
  }
  if (start + perPage < SUPPORTED_LANGUAGES.length) {
    navRow.push({ text: "Next ▶️", callback_data: `${CALLBACK.LANGS_PAGE}_${page + 1}` });
  }
  if (navRow.length) rows.push(navRow);

  rows.push([{ text: "🏠 Main Menu", callback_data: CALLBACK.MENU }]);

  return { inline_keyboard: rows };
}

export function aboutKeyboard(): TelegramBot.InlineKeyboardMarkup {
  return {
    inline_keyboard: [
      [
        { text: "🤗 HuggingFace Demo", url: "https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo" },
      ],
      [
        { text: "📦 GitHub Repo", url: "https://github.com/OpenBMB/VoxCPM" },
        { text: "🧠 Model Weights", url: "https://huggingface.co/openbmb/VoxCPM2" },
      ],
      [{ text: "🏠 Main Menu", callback_data: CALLBACK.MENU }],
    ],
  };
}

export function ttsReadyKeyboard(): TelegramBot.InlineKeyboardMarkup {
  return {
    inline_keyboard: [
      [
        { text: "🔄 Generate Another", callback_data: CALLBACK.TTS },
        { text: "🏠 Main Menu", callback_data: CALLBACK.MENU },
      ],
    ],
  };
}
