import io
import logging
import httpx
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import (
    main_menu_keyboard,
    cancel_keyboard,
    back_menu_keyboard,
    after_generate_keyboard,
    languages_keyboard,
    about_keyboard,
    voice_preview_list_keyboard,
    after_voice_preview_keyboard,
    use_voice_done_keyboard,
)
from constants import (
    SUPPORTED_LANGUAGES,
    PRESET_VOICES,
    STATE_IDLE,
    STATE_TTS_AWAITING_TEXT,
    STATE_VD_AWAITING_INSTRUCTION,
    STATE_VD_AWAITING_TEXT,
    STATE_VC_AWAITING_AUDIO,
    STATE_VC_AWAITING_TEXT,
    STATE_VP_AWAITING_TEXT,
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
    "• 🎭 Voice Preview — browse & hear 12 preset voice styles\n"
    "• 🎛️ Controllable Cloning — clone any voice\n"
    "• 🎙️ Ultimate Cloning — reproduce every vocal nuance\n"
    "• 🔊 48kHz studio\\-quality audio\n\n"
    "📜 Open\\-source under *Apache 2\\.0* license"
)

HELP_TEXT = (
    "❓ *How to use VoxCPM Bot:*\n\n"
    "*🗣️ Text\\-to\\-Speech \\(TTS\\)*\n"
    "Send any text — get speech back as a voice message\\. 30 languages auto\\-detected\\!\n\n"
    "*🎭 Voice Preview*\n"
    "Browse 12 preset voices \\(Narrator, Child, Elder, Robot…\\)\\. "
    "Tap any voice to hear a sample, then use it with your own text\\.\n\n"
    "*🎨 Voice Design*\n"
    "Describe a custom voice \\(age, gender, emotion, tone\\), then send text to speak\\.\n\n"
    "*🎙️ Voice Clone*\n"
    "Send a reference audio clip, then send text to speak in that cloned voice\\.\n\n"
    "*🌍 Languages*\n"
    "Browse all 30 supported languages\\.\n\n"
    "💡 *Tip:* VoxCPM2 auto\\-detects language — no tag needed\\!"
)


def _get_state(context: ContextTypes.DEFAULT_TYPE) -> int:
    return context.user_data.get("state", STATE_IDLE)


def _set_state(context: ContextTypes.DEFAULT_TYPE, state: int) -> None:
    context.user_data["state"] = state


def _clear(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()


def _find_voice(voice_id: str) -> dict | None:
    return next((v for v in PRESET_VOICES if v["id"] == voice_id), None)


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

    # ── Navigation ──────────────────────────────────────────────────────────
    if data == "menu":
        _clear(context)
        await context.bot.send_message(
            chat_id, WELCOME_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(),
        )
        return

    if data == "cancel":
        _clear(context)
        await context.bot.send_message(
            chat_id, "✅ Cancelled\\. Back to main menu:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_keyboard(),
        )
        return

    # ── TTS ──────────────────────────────────────────────────────────────────
    if data == "tts":
        _clear(context)
        _set_state(context, STATE_TTS_AWAITING_TEXT)
        await context.bot.send_message(
            chat_id,
            (
                "🗣️ *Text\\-to\\-Speech Mode*\n\n"
                "Send me any text and I'll convert it to a voice message\\.\n\n"
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

    # ── Voice Design ─────────────────────────────────────────────────────────
    if data == "vd":
        _clear(context)
        _set_state(context, STATE_VD_AWAITING_INSTRUCTION)
        await context.bot.send_message(
            chat_id,
            (
                "🎨 *Voice Design Mode*\n\n"
                "Describe the voice you want to create\\. Be creative\\!\n\n"
                "💡 *Examples:*\n"
                "• _\"A young woman with a soft, warm voice\\. Speaks slowly and gently\\.\"_\n"
                "• _\"An elderly man with a deep, wise voice\\. Speaks thoughtfully\\.\"_\n"
                "• _\"An energetic teenager, fast\\-paced and enthusiastic\\.\"_\n\n"
                "Send your *voice description* now:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(),
        )
        return

    # ── Voice Clone ──────────────────────────────────────────────────────────
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

    # ── Voice Preview — list page ─────────────────────────────────────────────
    if data.startswith("vp_") and not data.startswith("vp_listen_") and not data.startswith("vp_use_"):
        page = int(data.split("_")[1])
        total = len(PRESET_VOICES)
        await context.bot.send_message(
            chat_id,
            (
                f"🎭 *Voice Preview Gallery*\n\n"
                f"Browse {total} preset voice styles\\. "
                f"Tap any voice to hear a sample, then use it with your own text\\.\n\n"
                f"_Page {page + 1} of {(total - 1) // 6 + 1}_"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=voice_preview_list_keyboard(page),
        )
        return

    # ── Voice Preview — generate sample ──────────────────────────────────────
    if data.startswith("vp_listen_"):
        voice_id = data[len("vp_listen_"):]
        voice = _find_voice(voice_id)
        if not voice:
            await context.bot.send_message(chat_id, "❌ Voice not found\\.", parse_mode=ParseMode.MARKDOWN_V2)
            return
        await _do_voice_preview(context, chat_id, voice)
        return

    # ── Voice Preview — use this voice for custom text ────────────────────────
    if data.startswith("vp_use_"):
        voice_id = data[len("vp_use_"):]
        voice = _find_voice(voice_id)
        if not voice:
            await context.bot.send_message(chat_id, "❌ Voice not found\\.", parse_mode=ParseMode.MARKDOWN_V2)
            return
        _clear(context)
        context.user_data["instruction"] = voice["instruction"]
        context.user_data["vp_voice_id"] = voice_id
        _set_state(context, STATE_VP_AWAITING_TEXT)
        await context.bot.send_message(
            chat_id,
            (
                f"{voice['emoji']} *{_esc(voice['name'])} — Custom Text*\n\n"
                f"Voice style: _{_esc(voice['instruction'][:120])}_\n\n"
                f"Now send the *text you want spoken* in this voice:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_keyboard(),
        )
        return

    # ── Languages ─────────────────────────────────────────────────────────────
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
                f"✅ *{_esc(name)}* is supported\\!\n\nJust type text in that language and use *Text\\-to\\-Speech* — VoxCPM2 will auto\\-detect it\\!",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=back_menu_keyboard(),
            )
        return

    # ── About / Help ──────────────────────────────────────────────────────────
    if data == "about":
        await context.bot.send_message(
            chat_id, ABOUT_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=about_keyboard(),
        )
        return

    if data == "help":
        await context.bot.send_message(
            chat_id, HELP_TEXT,
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
        await msg.reply_text("👋 Use the menu to get started:", reply_markup=main_menu_keyboard())
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

    if state == STATE_VP_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ Please send a text message\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
            return
        instruction = context.user_data.get("instruction", "")
        voice_id = context.user_data.get("vp_voice_id", "")
        _clear(context)
        await _do_voice_design(
            context, chat_id, msg.text, instruction,
            done_keyboard=use_voice_done_keyboard(),
        )
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
            async with httpx.AsyncClient(timeout=30) as client:
                dl = await client.get(file.file_path)
                dl.raise_for_status()
                audio_bytes = dl.content

            context.user_data["ref_audio_bytes"] = audio_bytes
            context.user_data["ref_audio_name"] = (
                getattr(msg.voice, "mime_type", None) and "ref.ogg"
                or getattr(msg.audio, "file_name", None)
                or "ref.ogg"
            )
            _set_state(context, STATE_VC_AWAITING_TEXT)
            await msg.reply_text(
                f"✅ Reference audio received \\({len(audio_bytes) // 1024} KB\\)\\!\n\nNow send the *text you want spoken* in that voice:",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=cancel_keyboard(),
            )
        except Exception as exc:
            logger.error("Failed to download reference audio: %s", exc)
            await msg.reply_text("❌ Could not process the audio\\. Please try again\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
        return

    if state == STATE_VC_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ Please send a text message\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_keyboard())
            return
        ref_bytes = context.user_data.get("ref_audio_bytes", b"")
        ref_name = context.user_data.get("ref_audio_name", "ref.ogg")
        _clear(context)
        await _do_voice_clone(context, chat_id, msg.text, ref_bytes, ref_name)
        return


# ── Helpers ────────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Escape special MarkdownV2 characters."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


async def _do_tts(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str) -> None:
    short = text[:120] + ("…" if len(text) > 120 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ Generating speech…\n\n_{_esc(short)}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text)
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(
        context, chat_id, result,
        caption=f"🔊 *VoxCPM2 TTS*\n_{_esc(text[:200])}_",
    )


async def _do_voice_design(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    instruction: str,
    done_keyboard=None,
) -> None:
    short_i = instruction[:80] + ("…" if len(instruction) > 80 else "")
    short_t = text[:80] + ("…" if len(text) > 80 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ *Creating custom voice…*\n\n🎨 _{_esc(short_i)}_\n📝 _{_esc(short_t)}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text, instruction=instruction)
    await _safe_delete(context, chat_id, processing.message_id)
    caption = f"🎨 *Voice Generated\\!*\n\n🎭 _{_esc(instruction[:100])}_\n📝 _{_esc(text[:100])}_"
    await _send_audio_result(context, chat_id, result, caption=caption, keyboard=done_keyboard)


async def _do_voice_clone(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    ref_bytes: bytes,
    ref_name: str = "ref.ogg",
) -> None:
    short_t = text[:80] + ("…" if len(text) > 80 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ *Cloning voice…*\n\n📝 _{_esc(short_t)}_\n\nUploading reference audio and generating…",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text, reference_audio_bytes=ref_bytes, reference_audio_filename=ref_name)
    await _safe_delete(context, chat_id, processing.message_id)
    caption = f"🎙️ *Voice Clone*\n\n📝 _{_esc(text[:150])}_"
    await _send_audio_result(context, chat_id, result, caption=caption)


async def _do_voice_preview(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    voice: dict,
) -> None:
    """Generate a preview sample for a preset voice."""
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ Generating preview for *{_esc(voice['name'])}*…\n\n_{_esc(voice['instruction'][:100])}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=voice["sample"], instruction=voice["instruction"])
    await _safe_delete(context, chat_id, processing.message_id)

    if result.get("error") or not result.get("audio_url"):
        err_detail = _esc(str(result.get("error", "Unknown"))[:160])
        await context.bot.send_message(
            chat_id,
            f"❌ *Preview failed*\n\n_{err_detail}_",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_voice_preview_keyboard(voice["id"]),
        )
        return

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            dl = await client.get(result["audio_url"])
            dl.raise_for_status()
            audio_bytes = dl.content

        voice_file = InputFile(io.BytesIO(audio_bytes), filename="preview.ogg")
        caption = (
            f"{voice['emoji']} *{_esc(voice['name'])}*\n\n"
            f"_{_esc(voice['instruction'][:120])}_\n\n"
            f"📝 _{_esc(voice['sample'][:120])}_"
        )
        await context.bot.send_voice(
            chat_id,
            voice=voice_file,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_voice_preview_keyboard(voice["id"]),
        )
    except Exception as exc:
        logger.error("Failed to send preview voice: %s", exc)
        await context.bot.send_message(
            chat_id,
            "❌ Could not deliver preview\\. Please try again\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_voice_preview_keyboard(voice["id"]),
        )


async def _send_audio_result(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    result: dict,
    caption: str,
    keyboard=None,
) -> None:
    kb = keyboard or after_generate_keyboard()
    if result.get("error") or not result.get("audio_url"):
        err_detail = _esc(str(result.get("error", "Unknown error"))[:180])
        await context.bot.send_message(
            chat_id,
            (
                "❌ *Generation failed*\n\n"
                f"_{err_detail}_\n\n"
                "Try the live demo: [HuggingFace Space](https://huggingface\\.co/spaces/OpenBMB/VoxCPM\\-Demo)"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=kb,
            disable_web_page_preview=True,
        )
        return

    audio_url = result["audio_url"]
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            dl = await client.get(audio_url)
            dl.raise_for_status()
            audio_bytes = dl.content

        voice_file = InputFile(io.BytesIO(audio_bytes), filename="speech.ogg")
        await context.bot.send_voice(
            chat_id,
            voice=voice_file,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=kb,
        )
    except Exception as exc:
        logger.error("Failed to send voice: %s", exc)
        await context.bot.send_message(
            chat_id,
            "❌ Could not deliver voice message\\. Please try again\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=kb,
        )


async def _safe_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> None:
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception:
        pass
