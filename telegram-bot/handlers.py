import logging
from telegram import Update, Message
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import (
    main_menu_keyboard,
    cancel_keyboard,
    back_menu_keyboard,
    after_generate_keyboard,
    languages_keyboard,
    about_keyboard,
)
from constants import (
    SUPPORTED_LANGUAGES,
    STATE_IDLE,
    STATE_TTS_AWAITING_TEXT,
    STATE_VD_AWAITING_INSTRUCTION,
    STATE_VD_AWAITING_TEXT,
    STATE_VC_AWAITING_AUDIO,
    STATE_VC_AWAITING_TEXT,
)
from voxcpm_api import generate_speech

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "🎙️ *Welcome to VoxCPM Bot\\!*\n\n"
    "Powered by *VoxCPM2* — a tokenizer\\-free Text\\-to\\-Speech AI "
    "supporting *30 languages* including Khmer 🇰🇭\n\n"
    "Choose what you'd like to do:"
)

ABOUT_TEXT = (
    "🧠 *VoxCPM2 — Advanced TTS AI*\n\n"
    "VoxCPM2 is a 2B parameter model trained on over *2 million hours* of multilingual speech data\\.\n\n"
    "✨ *Features:*\n"
    "• 🌍 30 languages \\(including Khmer, Thai, Lao, Vietnamese…\\)\n"
    "• 🎨 Voice Design — create a voice from text description\n"
    "• 🎛️ Controllable Cloning — clone any voice\n"
    "• 🎙️ Ultimate Cloning — reproduce every vocal nuance\n"
    "• 🔊 48kHz studio\\-quality audio\n\n"
    "📜 Open\\-source under *Apache 2\\.0* license"
)

HELP_TEXT = (
    "❓ *How to use VoxCPM Bot:*\n\n"
    "*🗣️ Text\\-to\\-Speech \\(TTS\\)*\n"
    "Send any text and receive high\\-quality speech in any of 30 languages\\. Language is auto\\-detected\\!\n\n"
    "*🎨 Voice Design*\n"
    "Describe the voice you want \\(age, gender, emotion, tone\\), then send the text to speak\\.\n\n"
    "*🎙️ Voice Clone*\n"
    "Send a voice audio clip as reference, then provide the text to speak in that voice\\.\n\n"
    "*🌍 Languages*\n"
    "Browse all 30 supported languages \\(Khmer, Thai, Lao, Vietnamese, and more\\)\\.\n\n"
    "💡 *Tip:* VoxCPM2 auto\\-detects language — no tag needed\\!"
)


def _get_state(context: ContextTypes.DEFAULT_TYPE) -> int:
    return context.user_data.get("state", STATE_IDLE)


def _set_state(context: ContextTypes.DEFAULT_TYPE, state: int) -> None:
    context.user_data["state"] = state


def _clear(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clear(context)
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(),
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clear(context)
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=main_menu_keyboard(),
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    chat_id = query.message.chat_id

    if data == "menu":
        _clear(context)
        await context.bot.send_message(
            chat_id,
            WELCOME_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(),
        )
        return

    if data == "cancel":
        _clear(context)
        await context.bot.send_message(
            chat_id,
            "✅ Cancelled\\. Back to main menu:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(),
        )
        return

    if data == "tts":
        _clear(context)
        _set_state(context, STATE_TTS_AWAITING_TEXT)
        await context.bot.send_message(
            chat_id,
            (
                "🗣️ *Text\\-to\\-Speech Mode*\n\n"
                "Send me any text and I'll convert it to high\\-quality speech\\.\n\n"
                "💡 Supports *30 languages* — language is auto\\-detected\\!\n\n"
                "Examples:\n"
                "• _\"Hello, how are you today?\"_ \\(English\\)\n"
                "• _\"សួស្ដី\\! តើអ្នកសុខសប្បាយទេ?\"_ \\(Khmer\\)\n"
                "• _\"こんにちは、元気ですか？\"_ \\(Japanese\\)\n\n"
                "Send your text now:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(),
        )
        return

    if data == "vd":
        _clear(context)
        _set_state(context, STATE_VD_AWAITING_INSTRUCTION)
        await context.bot.send_message(
            chat_id,
            (
                "🎨 *Voice Design Mode*\n\n"
                "Describe the voice you want to create\\. Be creative\\!\n\n"
                "💡 *Examples:*\n"
                "• _\"A young woman with a soft, warm voice\\. Speaks slowly and gently with a calming tone\\.\"_\n"
                "• _\"An elderly man with a deep, wise voice\\. Speaks slowly and thoughtfully\\.\"_\n"
                "• _\"An energetic teenager, fast\\-paced and enthusiastic\\.\"_\n\n"
                "Send your *voice description* now:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(),
        )
        return

    if data == "vc":
        _clear(context)
        _set_state(context, STATE_VC_AWAITING_AUDIO)
        await context.bot.send_message(
            chat_id,
            (
                "🎙️ *Voice Clone Mode*\n\n"
                "Send a *voice message* or *audio file* as reference \\(3–30 seconds recommended\\)\\.\n\n"
                "VoxCPM2 will clone the voice and speak any text in that style\\.\n\n"
                "📎 Send your *reference audio* now:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(),
        )
        return

    if data.startswith("langs_"):
        page = int(data.split("_")[1])
        await context.bot.send_message(
            chat_id,
            "🌍 *Supported Languages \\(30\\)*\n\nVoxCPM2 automatically detects and synthesizes speech in all these languages:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=languages_keyboard(page),
        )
        return

    if data.startswith("lang_"):
        code = data[5:]
        lang = next((l for l in SUPPORTED_LANGUAGES if l["code"] == code), None)
        if lang:
            name = lang["name"]
            await context.bot.send_message(
                chat_id,
                f"✅ *{name}* is supported\\!\n\nJust type text in that language and use *Text\\-to\\-Speech* — VoxCPM2 will auto\\-detect it\\!",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=back_menu_keyboard(),
            )
        return

    if data == "about":
        await context.bot.send_message(
            chat_id,
            ABOUT_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=about_keyboard(),
        )
        return

    if data == "help":
        await context.bot.send_message(
            chat_id,
            HELP_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(),
        )
        return


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg:
        return

    state = _get_state(context)
    chat_id = msg.chat_id

    if state == STATE_IDLE:
        await msg.reply_text(
            "👋 Use the menu to get started:",
            reply_markup=main_menu_keyboard(),
        )
        return

    if state == STATE_TTS_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ Please send a text message\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
            return
        _clear(context)
        await _do_tts(context, chat_id, msg.text)
        return

    if state == STATE_VD_AWAITING_INSTRUCTION:
        if not msg.text:
            await msg.reply_text("⚠️ Please send a text description\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
            return
        context.user_data["instruction"] = msg.text
        _set_state(context, STATE_VD_AWAITING_TEXT)
        short = msg.text[:80] + ("…" if len(msg.text) > 80 else "")
        await msg.reply_text(
            f"✅ Voice description saved\\!\n\n_\"{_esc(short)}\"_\n\nNow send the *text you want spoken* in this voice:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(),
        )
        return

    if state == STATE_VD_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ Please send a text message\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
            return
        instruction = context.user_data.get("instruction", "")
        _clear(context)
        await _do_voice_design(context, chat_id, msg.text, instruction)
        return

    if state == STATE_VC_AWAITING_AUDIO:
        file_id = None
        if msg.voice:
            file_id = msg.voice.file_id
        elif msg.audio:
            file_id = msg.audio.file_id
        elif msg.document:
            file_id = msg.document.file_id

        if not file_id:
            await msg.reply_text(
                "⚠️ Please send a *voice message* or *audio file* as your reference\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=cancel_keyboard(),
            )
            return

        try:
            file = await context.bot.get_file(file_id)
            context.user_data["ref_audio_url"] = file.file_path
            _set_state(context, STATE_VC_AWAITING_TEXT)
            await msg.reply_text(
                "✅ Reference audio received\\!\n\nNow send the *text you want spoken* in that voice:",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=cancel_keyboard(),
            )
        except Exception as exc:
            logger.error("Failed to get file: %s", exc)
            await msg.reply_text("❌ Could not process the audio\\. Please try again\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
        return

    if state == STATE_VC_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ Please send a text message\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
            return
        ref_url = context.user_data.get("ref_audio_url", "")
        _clear(context)
        await _do_voice_clone(context, chat_id, msg.text, ref_url)
        return


def _esc(text: str) -> str:
    """Escape special MarkdownV2 characters."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


async def _do_tts(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str) -> None:
    short = text[:120] + ("…" if len(text) > 120 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ Generating speech for:\n_{_esc(short)}_\n\nThis may take a few seconds…",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text)
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(context, chat_id, result, caption=f"🔊 *VoxCPM2 TTS*\n_{_esc(text[:200])}_")


async def _do_voice_design(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, instruction: str) -> None:
    short_i = instruction[:80] + ("…" if len(instruction) > 80 else "")
    short_t = text[:80] + ("…" if len(text) > 80 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ *Creating custom voice…*\n\n🎨 Voice: _{_esc(short_i)}_\n📝 Text: _{_esc(short_t)}_\n\nThis may take a few seconds…",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text, instruction=instruction)
    await _safe_delete(context, chat_id, processing.message_id)
    caption = f"🎨 *Custom Voice Generated\\!*\n\n🎭 Voice: _{_esc(instruction[:100])}_\n📝 Text: _{_esc(text[:100])}_"
    await _send_audio_result(context, chat_id, result, caption=caption)


async def _do_voice_clone(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, ref_url: str) -> None:
    short_t = text[:80] + ("…" if len(text) > 80 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ *Cloning voice…*\n\n📝 Text: _{_esc(short_t)}_\n\nThis may take a few seconds…",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text, reference_audio_url=ref_url)
    await _safe_delete(context, chat_id, processing.message_id)
    caption = f"🎙️ *Voice Clone Generated\\!*\n\n📝 Text: _{_esc(text[:150])}_"
    await _send_audio_result(context, chat_id, result, caption=caption)


async def _send_audio_result(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    result: dict,
    caption: str,
) -> None:
    if result.get("error") or not result.get("audio_url"):
        await context.bot.send_message(
            chat_id,
            (
                "❌ *Generation failed*\n\n"
                "The VoxCPM demo server may be busy or unavailable\\.\n\n"
                f"Try the live demo: [HuggingFace Space](https://huggingface.co/spaces/OpenBMB/VoxCPM\\-Demo)"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_generate_keyboard(),
            disable_web_page_preview=True,
        )
        return

    audio_url = result["audio_url"]
    try:
        await context.bot.send_audio(
            chat_id,
            audio=audio_url,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_generate_keyboard(),
        )
    except Exception:
        await context.bot.send_message(
            chat_id,
            f"🔊 Audio generated\\!\n\n[Download Audio]({_esc(audio_url)})",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_generate_keyboard(),
        )


async def _safe_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> None:
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception:
        pass
