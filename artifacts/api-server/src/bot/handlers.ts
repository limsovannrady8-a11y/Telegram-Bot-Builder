import TelegramBot from "node-telegram-bot-api";
import { logger } from "../lib/logger.js";
import { getSession, setSession, resetSession } from "./session.js";
import {
  mainMenuKeyboard,
  backToMenuKeyboard,
  cancelKeyboard,
  languagesKeyboard,
  aboutKeyboard,
  ttsReadyKeyboard,
} from "./keyboards.js";
import { CALLBACK, STEPS, MODES, SUPPORTED_LANGUAGES } from "./constants.js";
import { generateSpeech } from "./voxcpm-api.js";

const WELCOME_TEXT = `🎙️ *Welcome to VoxCPM Bot!*

Powered by *VoxCPM2* — a tokenizer-free Text-to-Speech AI supporting *30 languages* including Khmer 🇰🇭

Choose what you'd like to do:`;

const ABOUT_TEXT = `🧠 *VoxCPM2 — Advanced TTS AI*

VoxCPM2 is a 2B parameter model trained on over *2 million hours* of multilingual speech data.

✨ *Features:*
• 🌍 30 languages (including Khmer, Thai, Lao, Vietnamese and more)
• 🎨 Voice Design — create a voice from text description
• 🎛️ Controllable Cloning — clone any voice
• 🎙️ Ultimate Cloning — reproduce every vocal nuance
• 🔊 48kHz studio-quality audio

📜 Open-source under *Apache 2.0* license`;

const HELP_TEXT = `❓ *How to use VoxCPM Bot:*

*🗣️ Text-to-Speech (TTS)*
Simply send text and get high-quality speech generated in any of the 30 supported languages.

*🎨 Voice Design*
Describe the voice you want (gender, age, emotion, tone) then provide the text. VoxCPM2 creates a unique voice from your description.

*🎙️ Voice Clone*
Send a voice audio clip as reference, then provide the text you want spoken in that voice.

*🌍 Languages*
See all 30 supported languages. VoxCPM2 auto-detects the language from your text.

💡 *Tip:* VoxCPM2 auto-detects language from your input text — no need to specify!`;

export function registerHandlers(bot: TelegramBot): void {
  bot.on("message", async (msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from?.id ?? chatId;
    const session = getSession(userId);

    if (msg.text?.startsWith("/start")) {
      resetSession(userId);
      await bot.sendMessage(chatId, WELCOME_TEXT, {
        parse_mode: "Markdown",
        reply_markup: mainMenuKeyboard(),
      });
      return;
    }

    if (msg.text?.startsWith("/help")) {
      await bot.sendMessage(chatId, HELP_TEXT, {
        parse_mode: "Markdown",
        reply_markup: mainMenuKeyboard(),
      });
      return;
    }

    if (msg.text?.startsWith("/menu") || msg.text?.startsWith("/start")) {
      resetSession(userId);
      await bot.sendMessage(chatId, WELCOME_TEXT, {
        parse_mode: "Markdown",
        reply_markup: mainMenuKeyboard(),
      });
      return;
    }

    if (session.step === STEPS.AWAITING_TEXT && session.mode === MODES.TTS) {
      if (!msg.text) {
        await bot.sendMessage(chatId, "⚠️ Please send a text message.", {
          reply_markup: cancelKeyboard(),
        });
        return;
      }
      await handleTtsGenerate(bot, chatId, userId, msg.text);
      return;
    }

    if (session.step === STEPS.AWAITING_INSTRUCTION && session.mode === MODES.VOICE_DESIGN) {
      if (!msg.text) {
        await bot.sendMessage(chatId, "⚠️ Please send a text description.", {
          reply_markup: cancelKeyboard(),
        });
        return;
      }
      setSession(userId, {
        step: STEPS.AWAITING_INSTRUCTION_THEN_TEXT,
        pendingInstruction: msg.text,
      });
      await bot.sendMessage(
        chatId,
        `✅ Voice description saved!\n\n*"${msg.text}"*\n\nNow send the *text you want spoken* in this voice:`,
        { parse_mode: "Markdown", reply_markup: cancelKeyboard() },
      );
      return;
    }

    if (
      session.step === STEPS.AWAITING_INSTRUCTION_THEN_TEXT &&
      session.mode === MODES.VOICE_DESIGN
    ) {
      if (!msg.text) {
        await bot.sendMessage(chatId, "⚠️ Please send a text message.", {
          reply_markup: cancelKeyboard(),
        });
        return;
      }
      await handleVoiceDesignGenerate(bot, chatId, userId, msg.text, session.pendingInstruction ?? "");
      return;
    }

    if (session.step === STEPS.AWAITING_AUDIO && session.mode === MODES.VOICE_CLONE) {
      if (!msg.voice && !msg.audio && !msg.document) {
        await bot.sendMessage(
          chatId,
          "⚠️ Please send a *voice message* or *audio file* as your reference.",
          { parse_mode: "Markdown", reply_markup: cancelKeyboard() },
        );
        return;
      }
      const fileId = msg.voice?.file_id ?? msg.audio?.file_id ?? msg.document?.file_id;
      if (!fileId) return;
      try {
        const fileLink = await bot.getFileLink(fileId);
        setSession(userId, {
          step: STEPS.AWAITING_AUDIO_TEXT,
          pendingInstruction: fileLink,
        });
        await bot.sendMessage(
          chatId,
          "✅ Reference audio received!\n\nNow send the *text you want spoken* in that voice:",
          { parse_mode: "Markdown", reply_markup: cancelKeyboard() },
        );
      } catch (err) {
        logger.error({ err }, "Failed to get file link");
        await bot.sendMessage(chatId, "❌ Could not process the audio. Please try again.", {
          reply_markup: cancelKeyboard(),
        });
      }
      return;
    }

    if (session.step === STEPS.AWAITING_AUDIO_TEXT && session.mode === MODES.VOICE_CLONE) {
      if (!msg.text) {
        await bot.sendMessage(chatId, "⚠️ Please send a text message.", {
          reply_markup: cancelKeyboard(),
        });
        return;
      }
      await handleVoiceCloneGenerate(bot, chatId, userId, msg.text, session.pendingInstruction ?? "");
      return;
    }

    if (session.step === STEPS.IDLE) {
      await bot.sendMessage(chatId, "👋 Use the menu to get started:", {
        reply_markup: mainMenuKeyboard(),
      });
    }
  });

  bot.on("callback_query", async (query) => {
    const chatId = query.message?.chat.id;
    const userId = query.from.id;
    const data = query.data ?? "";

    if (!chatId) return;
    await bot.answerCallbackQuery(query.id);

    if (data === CALLBACK.MENU) {
      resetSession(userId);
      await bot.sendMessage(chatId, WELCOME_TEXT, {
        parse_mode: "Markdown",
        reply_markup: mainMenuKeyboard(),
      });
      return;
    }

    if (data === CALLBACK.CANCEL) {
      resetSession(userId);
      await bot.sendMessage(chatId, "✅ Cancelled. Back to main menu:", {
        reply_markup: mainMenuKeyboard(),
      });
      return;
    }

    if (data === CALLBACK.TTS) {
      setSession(userId, { step: STEPS.AWAITING_TEXT, mode: MODES.TTS });
      await bot.sendMessage(
        chatId,
        `🗣️ *Text-to-Speech Mode*\n\nSend me any text and I'll convert it to high-quality speech.\n\n💡 Supports *30 languages* — VoxCPM2 auto-detects your language!\n\nExamples:\n• _"Hello, how are you today?"_ (English)\n• _"សួស្ដី! តើអ្នកសុខសប្បាយទេ?"_ (Khmer)\n• _"こんにちは、元気ですか？"_ (Japanese)`,
        { parse_mode: "Markdown", reply_markup: cancelKeyboard() },
      );
      return;
    }

    if (data === CALLBACK.VOICE_DESIGN) {
      setSession(userId, { step: STEPS.AWAITING_INSTRUCTION, mode: MODES.VOICE_DESIGN });
      await bot.sendMessage(
        chatId,
        `🎨 *Voice Design Mode*\n\nDescribe the voice you want to create. Be creative!\n\n💡 *Examples:*\n• _"A young woman with a soft, warm voice. Speaks slowly and gently with a calming tone."_\n• _"An elderly man with a deep, wise voice. Speaks slowly and thoughtfully."_\n• _"An energetic teenager, fast-paced and enthusiastic."_\n\nSend your *voice description*:`,
        { parse_mode: "Markdown", reply_markup: cancelKeyboard() },
      );
      return;
    }

    if (data === CALLBACK.VOICE_CLONE) {
      setSession(userId, { step: STEPS.AWAITING_AUDIO, mode: MODES.VOICE_CLONE });
      await bot.sendMessage(
        chatId,
        `🎙️ *Voice Clone Mode*\n\nSend a *voice message* or *audio file* as your reference (3–30 seconds recommended).\n\nVoxCPM2 will clone the voice from your audio and speak any text in that style.\n\n📎 Send your *reference audio* now:`,
        { parse_mode: "Markdown", reply_markup: cancelKeyboard() },
      );
      return;
    }

    if (data === CALLBACK.LANGUAGES) {
      await bot.sendMessage(
        chatId,
        `🌍 *Supported Languages (30)*\n\nVoxCPM2 automatically detects and synthesizes speech in all these languages:`,
        { parse_mode: "Markdown", reply_markup: languagesKeyboard(0) },
      );
      return;
    }

    if (data.startsWith(`${CALLBACK.LANGS_PAGE}_`)) {
      const page = parseInt(data.split("_").pop() ?? "0", 10);
      await bot.editMessageReplyMarkup(languagesKeyboard(page), {
        chat_id: chatId,
        message_id: query.message?.message_id,
      });
      return;
    }

    if (data.startsWith("lang_")) {
      const code = data.replace("lang_", "");
      const lang = SUPPORTED_LANGUAGES.find((l) => l.code === code);
      if (lang) {
        await bot.sendMessage(
          chatId,
          `${lang.name} is supported! 🎉\n\nJust type or paste text in ${lang.name.replace(/\s+🇨🇳|🇰🇭|🇬🇧|🇯🇵|🇰🇷|🇫🇷|🇩🇪|🇪🇸|🇮🇳|🇸🇦|🇷🇺|🇹🇭|🇻🇳|🇮🇩|🇧🇷|🇹🇷|🇵🇱|🇳🇱|🇮🇹|🇱🇦/g, "").trim()} and use *Text-to-Speech* — VoxCPM2 will auto-detect it!`,
          { parse_mode: "Markdown", reply_markup: backToMenuKeyboard() },
        );
      }
      return;
    }

    if (data === CALLBACK.ABOUT) {
      await bot.sendMessage(chatId, ABOUT_TEXT, {
        parse_mode: "Markdown",
        reply_markup: aboutKeyboard(),
      });
      return;
    }

    if (data === CALLBACK.HELP) {
      await bot.sendMessage(chatId, HELP_TEXT, {
        parse_mode: "Markdown",
        reply_markup: mainMenuKeyboard(),
      });
      return;
    }
  });

  bot.on("polling_error", (err) => {
    logger.error({ err }, "Telegram polling error");
  });
}

async function handleTtsGenerate(
  bot: TelegramBot,
  chatId: number,
  userId: number,
  text: string,
): Promise<void> {
  resetSession(userId);
  const processing = await bot.sendMessage(
    chatId,
    `⏳ Generating speech for:\n_"${text.slice(0, 120)}${text.length > 120 ? "…" : ""}"_\n\nThis may take a few seconds...`,
    { parse_mode: "Markdown" },
  );

  const result = await generateSpeech({ text });

  await bot.deleteMessage(chatId, processing.message_id).catch(() => {});

  if (result.error || !result.audioUrl) {
    await bot.sendMessage(
      chatId,
      `❌ *Generation failed*\n\nThe VoxCPM demo server may be busy or unavailable.\n\nTry the live demo directly: [HuggingFace Space](https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo)`,
      { parse_mode: "Markdown", reply_markup: ttsReadyKeyboard() },
    );
    return;
  }

  try {
    await bot.sendAudio(chatId, result.audioUrl, {
      caption: `🔊 *VoxCPM2 TTS*\n_"${text.slice(0, 200)}${text.length > 200 ? "…" : ""}"_`,
      parse_mode: "Markdown",
      reply_markup: ttsReadyKeyboard(),
    });
  } catch {
    await bot.sendMessage(
      chatId,
      `🔊 Audio generated!\n\n[Download Audio](${result.audioUrl})\n\nText: _"${text.slice(0, 200)}"_`,
      { parse_mode: "Markdown", reply_markup: ttsReadyKeyboard() },
    );
  }
}

async function handleVoiceDesignGenerate(
  bot: TelegramBot,
  chatId: number,
  userId: number,
  text: string,
  instruction: string,
): Promise<void> {
  resetSession(userId);
  const processing = await bot.sendMessage(
    chatId,
    `⏳ *Creating custom voice...*\n\n🎨 Voice: _"${instruction.slice(0, 80)}${instruction.length > 80 ? "…" : ""}"_\n📝 Text: _"${text.slice(0, 80)}${text.length > 80 ? "…" : ""}"_\n\nThis may take a few seconds...`,
    { parse_mode: "Markdown" },
  );

  const result = await generateSpeech({ text, instruction });

  await bot.deleteMessage(chatId, processing.message_id).catch(() => {});

  if (result.error || !result.audioUrl) {
    await bot.sendMessage(
      chatId,
      `❌ *Generation failed*\n\nThe VoxCPM demo server may be busy.\n\nTry the live demo: [HuggingFace Space](https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo)`,
      { parse_mode: "Markdown", reply_markup: mainMenuKeyboard() },
    );
    return;
  }

  try {
    await bot.sendAudio(chatId, result.audioUrl, {
      caption: `🎨 *Custom Voice Generated!*\n\n🎭 Voice style: _"${instruction.slice(0, 100)}"_\n📝 Text: _"${text.slice(0, 100)}"_`,
      parse_mode: "Markdown",
      reply_markup: mainMenuKeyboard(),
    });
  } catch {
    await bot.sendMessage(
      chatId,
      `🎨 Custom voice generated!\n\n[Download Audio](${result.audioUrl})`,
      { parse_mode: "Markdown", reply_markup: mainMenuKeyboard() },
    );
  }
}

async function handleVoiceCloneGenerate(
  bot: TelegramBot,
  chatId: number,
  userId: number,
  text: string,
  referenceAudioUrl: string,
): Promise<void> {
  resetSession(userId);
  const processing = await bot.sendMessage(
    chatId,
    `⏳ *Cloning voice...*\n\n📝 Text: _"${text.slice(0, 80)}${text.length > 80 ? "…" : ""}"_\n\nThis may take a few seconds...`,
    { parse_mode: "Markdown" },
  );

  const result = await generateSpeech({ text, referenceAudioUrl });

  await bot.deleteMessage(chatId, processing.message_id).catch(() => {});

  if (result.error || !result.audioUrl) {
    await bot.sendMessage(
      chatId,
      `❌ *Voice cloning failed*\n\nThe VoxCPM demo server may be busy.\n\nTry the live demo: [HuggingFace Space](https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo)`,
      { parse_mode: "Markdown", reply_markup: mainMenuKeyboard() },
    );
    return;
  }

  try {
    await bot.sendAudio(chatId, result.audioUrl, {
      caption: `🎙️ *Voice Clone Generated!*\n\n📝 Text: _"${text.slice(0, 150)}"_`,
      parse_mode: "Markdown",
      reply_markup: mainMenuKeyboard(),
    });
  } catch {
    await bot.sendMessage(
      chatId,
      `🎙️ Voice clone generated!\n\n[Download Audio](${result.audioUrl})`,
      { parse_mode: "Markdown", reply_markup: mainMenuKeyboard() },
    );
  }
}
