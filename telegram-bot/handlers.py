import io
import logging
import os
import subprocess
import tempfile
import httpx
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import (
    main_menu_reply_keyboard,
    cancel_reply_keyboard,
    voice_list_reply_keyboard,
    voice_preview_reply_keyboard,
)
from constants import (
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
import db as voice_db

logger = logging.getLogger(__name__)

WELCOME_TEXT = "🎙️ *សូមស្វាគមន៍មកកាន់ Khmer Text To Voice*"

ABOUT_TEXT = (
    "🧠 *VoxCPM2 — AI TTS កម្រិតខ្ពស់*\n\n"
    "VoxCPM2 គឺជាម៉ូដែលដែលមាន 2B parameters "
    "ហើយត្រូវបានបណ្តុះបណ្តាលលើទិន្នន័យសំឡេងច្រើនជាង *2 លានម៉ោង*\\.\n\n"
    "✨ *មុខងារ:*\n"
    "• 🌍 ៣០ ភាសា \\(រួមមាន ខ្មែរ, ថៃ, ឡាវ, វៀតណាម…\\)\n"
    "• 🎨 រចនាសំឡេង — បង្កើតសំឡេងតាមការពិពណ៌នា\n"
    "• 🔊 ជ្រើសរើសសំឡេង — ស្ដាប់គំរូ 12 ប្រភេទសំឡេង\n"
    "• 🎛️ ក្លូនដែលអាចគ្រប់គ្រងបាន — ក្លូនសំឡេងណាមួយ\n"
    "• 🔊 សំឡេងគុណភាព studio 48kHz\n\n"
    "📜 Open\\-source ក្រោម *Apache 2\\.0*"
)

HELP_TEXT = (
    "❓ *របៀបប្រើ VoxCPM Bot:*\n\n"
    "*📝 អត្ថបទ → សំឡេង \\(TTS\\)*\n"
    "ផ្ញើអត្ថបទណាមួយ — ទទួលបានសំឡេង voice message ។ គាំទ្រ ៣០ ភាសា \\(auto\\-detected\\)\\!\n\n"
    "*🔊 ជ្រើសរើសសំឡេង*\n"
    "ស្ដាប់គំរូ 12 ប្រភេទសំឡេង \\(អ្នករំទឹប, កុមារ, ចាស់ទុំ, Robot…\\)\\. "
    "ចុចលើសំឡេងដើម្បីស្ដាប់ ហើយប្រើជាមួយអត្ថបទខ្លួនឯង\\.\n\n"
    "*🎨 រចនាសំឡេង*\n"
    "ពិពណ៌នាសំឡេងដែលចង់បាន \\(អាយុ, ភេទ, អារម្មណ៍, សំណេរ\\) ហើយផ្ញើអត្ថបទ\\.\n\n"
    "*🎙️ ក្លូនសំឡេង*\n"
    "ផ្ញើ audio យោង ហើយផ្ញើអត្ថបទ ដើម្បីបង្កើតសំឡេងដូច\\.\n\n"
    "*🌍 ភាសា*\n"
    "ស្វែងរក ៣០ ភាសាដែលគាំទ្រ\\.\n\n"
    "💡 *គន្លឹះ:* VoxCPM2 រកភាសាដោយស្វ័យប្រវត្តិ — មិនចាំបាច់ tag\\!"
)


def _get_state(context: ContextTypes.DEFAULT_TYPE) -> int:
    return context.user_data.get("state", STATE_IDLE)


def _set_state(context: ContextTypes.DEFAULT_TYPE, state: int) -> None:
    context.user_data["state"] = state


def _clear(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()


def _find_voice(voice_id: str) -> dict | None:
    return next((v for v in PRESET_VOICES if v["id"] == voice_id), None)


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    chat_id = query.message.chat_id

    if data in ("menu", "cancel"):
        _clear(context)
        await context.bot.send_message(
            chat_id, WELCOME_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_reply_keyboard(),
        )
        return


async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg:
        return

    chat_id = msg.chat_id
    text = msg.text or ""

    # ── Commands always reset ────────────────────────────────────────────────
    if text.startswith("/"):
        _clear(context)
        await msg.reply_text(
            WELCOME_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_reply_keyboard(),
        )
        return

    # ── ReplyKeyboard menu button routing ────────────────────────────────────
    if text == "⬅️":
        import asyncio
        in_voice_preview = (
            "vp_current_idx" in context.user_data
            or _get_state(context) == STATE_VP_AWAITING_TEXT
        )
        _clear(context)

        if in_voice_preview:
            await context.bot.send_message(
                chat_id,
                "*សូមជ្រើសរើសប្រភេទសំឡេង:*",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=voice_list_reply_keyboard(),
            )
        else:
            await context.bot.send_message(
                chat_id,
                WELCOME_TEXT,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_reply_keyboard(),
            )
        return

    if text == "📝 អត្ថបទ → សំឡេង":
        _clear(context)
        _set_state(context, STATE_TTS_AWAITING_TEXT)
        await msg.reply_text(
            (
                "<b>អត្ថបទ → សំឡេង (Random Voice)</b>\n\n"
                '<tg-emoji emoji-id="5471978009449731768">👉</tg-emoji>'
                " ផ្ញើអត្ថបទណាមួយ ហើយខ្ញុំនឹងបំប្លែងជាសំឡេង:"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=cancel_reply_keyboard(),
        )
        return

    if text == "🎨 រចនាសំឡេង":
        _clear(context)
        _set_state(context, STATE_VD_AWAITING_INSTRUCTION)
        await msg.reply_text(
            (
                "🎨 *ម៉ូដ រចនាសំឡេង*\n\n"
                "ពិពណ៌នាអំពីសំឡេងដែលចង់បង្កើត\\. សូមបង្ហាញគំនិត\\!\n\n"
                "💡 *ឧទាហរណ៍:*\n"
                "• _\"ស្ត្រីក្មេង សំឡេងទន់ ។ និយាយយឺតៗ ស្ងប់ស្ងាត់\\.\"_\n"
                "• _\"បុរសចាស់ ប្រាជ្ញ ។ និយាយច្បាស់ ហ៊ានហ៊ឺន\\.\"_\n"
                "• _\"យុវវ័យ ថាមពលខ្លាំង ។ ប្រញាប់ ស្រស់ស្រាយ\\.\"_\n\n"
                "ផ្ញើ *ការពិពណ៌នា* របស់អ្នក:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_reply_keyboard(),
        )
        return

    if text == "🎙️ ក្លូនសំឡេង":
        _clear(context)
        _set_state(context, STATE_VC_AWAITING_AUDIO)
        await msg.reply_text(
            (
                "ផ្ញើ *voice message* ឬ *audio file* ជាឯកសារយោង \\(3–30 វិនាទីល្អបំផុត\\)\n\n"
                "👉 _ផ្ញើសំឡេងដែលអ្នកចង់ក្លូន_"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_reply_keyboard(),
        )
        return

    if text == "🔊 ជ្រើសរើសសំឡេង":
        await msg.reply_text(
            "*សូមជ្រើសរើសប្រភេទសំឡេង:*",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=voice_list_reply_keyboard(),
        )
        return

    # ── Voice name buttons ────────────────────────────────────────────────────
    _voice_match = next(
        (v for v in PRESET_VOICES if text == f"{v['emoji']} {v['name']}"), None
    )
    if _voice_match:
        idx = PRESET_VOICES.index(_voice_match)
        await _do_voice_preview(context, chat_id, _voice_match, idx=idx)
        return

    # ── Voice preview navigation / action buttons ─────────────────────────────

    if text == "✏️ ប្រើសំឡេងនេះ":
        idx = context.user_data.get("vp_current_idx", 0)
        voice = PRESET_VOICES[idx]
        voice_id = voice["id"]
        cached_bytes = context.bot_data.get(f"vp_cache_{voice_id}")
        if not cached_bytes:
            cached_bytes = await voice_db.get_cached_voice(voice_id)
        _clear(context)
        context.user_data["instruction"] = voice["instruction"]
        context.user_data["vp_voice_id"] = voice_id
        if cached_bytes:
            context.user_data["vp_ref_bytes"] = cached_bytes
        _set_state(context, STATE_VP_AWAITING_TEXT)
        await msg.reply_text(
            f"{voice['emoji']} *{_esc(voice['name'])}*\n\nផ្ញើ *អត្ថបទ* ដែលចង់និយាយ:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_reply_keyboard(),
        )
        return

    # ── State-based message handling ─────────────────────────────────────────
    state = _get_state(context)

    if state == STATE_IDLE:
        _clear(context)
        await msg.reply_text(
            WELCOME_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_reply_keyboard(),
        )
        return

    if state == STATE_TTS_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ សូមផ្ញើអត្ថបទ\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_reply_keyboard())
            return
        _clear(context)
        await _do_tts(context, chat_id, msg.text)
        return

    if state == STATE_VD_AWAITING_INSTRUCTION:
        if not msg.text:
            await msg.reply_text("⚠️ សូមផ្ញើអត្ថបទពិពណ៌នា\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_reply_keyboard())
            return
        context.user_data["instruction"] = msg.text
        _set_state(context, STATE_VD_AWAITING_TEXT)
        short = msg.text[:80] + ("…" if len(msg.text) > 80 else "")
        await msg.reply_text(
            f"✅ ការពិពណ៌នាបានរក្សាទុក\\!\n\n_\"{_esc(short)}\"_\n\nឥឡូវផ្ញើ *អត្ថបទ* ដែលចង់និយាយ:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_reply_keyboard(),
        )
        return

    if state == STATE_VD_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ សូមផ្ញើអត្ថបទ\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_reply_keyboard())
            return
        instruction = context.user_data.get("instruction", "")
        _clear(context)
        await _do_voice_design(context, chat_id, msg.text, instruction)
        return

    if state == STATE_VP_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ សូមផ្ញើអត្ថបទ\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_reply_keyboard())
            return
        instruction = context.user_data.get("instruction", "")
        voice_id = context.user_data.get("vp_voice_id", "")
        ref_bytes = context.user_data.get("vp_ref_bytes")
        _clear(context)
        await _do_vp_with_voice(context, chat_id, msg.text, instruction, ref_bytes, voice_id)
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
                "⚠️ សូមផ្ញើ *voice message* ឬ *audio file* ជាឯកសារយោង\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=cancel_reply_keyboard(),
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
                f"✅ បានទទួលសំឡេងរបស់អ្នកហើយ\n\n👉 _ឥឡូវផ្ញើអត្ថបទដែលចង់និយាយ:_",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=cancel_reply_keyboard(),
            )
        except Exception as exc:
            logger.error("Failed to download reference audio: %s", exc)
            await msg.reply_text("❌ មិនអាចដំណើរការ audio បាន\\. សូមព្យាយាមម្ដងទៀត\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_reply_keyboard())
        return

    if state == STATE_VC_AWAITING_TEXT:
        if not msg.text:
            await msg.reply_text("⚠️ សូមផ្ញើអត្ថបទ\\.", parse_mode=ParseMode.MARKDOWN_V2, reply_markup=cancel_reply_keyboard())
            return
        ref_bytes = context.user_data.get("ref_audio_bytes", b"")
        ref_name = context.user_data.get("ref_audio_name", "ref.ogg")
        _clear(context)
        await _do_voice_clone(context, chat_id, msg.text, ref_bytes, ref_name)
        return


# ── Helpers ────────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


def _is_khmer(text: str) -> bool:
    """Return True if the text contains a significant portion of Khmer characters."""
    if not text:
        return False
    khmer_chars = sum(1 for c in text if "\u1780" <= c <= "\u17FF")
    return khmer_chars / max(len(text.strip()), 1) > 0.15


KHMER_INSTRUCTION = (
    "Speak naturally and clearly in Khmer language (ភាសាខ្មែរ). "
    "Use authentic Khmer pronunciation with a calm, natural pace."
)


def _with_khmer_hint(instruction: str, text: str) -> str:
    """Append a Khmer language hint when text is Khmer and instruction lacks one."""
    if not _is_khmer(text):
        return instruction
    hint = "Speak naturally in Khmer language (ភាសាខ្មែរ). Use authentic Khmer pronunciation."
    if instruction:
        if _is_khmer(instruction):
            return instruction + " Speak in Khmer language (ភាសាខ្មែរ)."
        return instruction + " Speak in Khmer language (ភាសាខ្មែរ)."
    return hint


async def _do_tts(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str) -> None:
    processing = await context.bot.send_sticker(
        chat_id,
        sticker="CAACAgUAAxkBAAEDu4Zp-rTrlmnphDX-WIT9au-O6aW5CwACLRYAAvgG8VSjN2gKlvlMQTsE",
    )
    result = await generate_speech(text=text, instruction="")
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(
        context, chat_id, result,
        caption=None,
        keyboard=main_menu_reply_keyboard(),
    )


async def _do_voice_design(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    instruction: str,
    done_keyboard=None,
) -> None:
    processing = await context.bot.send_sticker(
        chat_id,
        sticker="CAACAgUAAxkBAAEDu4Zp-rTrlmnphDX-WIT9au-O6aW5CwACLRYAAvgG8VSjN2gKlvlMQTsE",
    )
    result = await generate_speech(text=text, instruction=_with_khmer_hint(instruction, text))
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(context, chat_id, result, caption="🎨 *សំឡេងបានបង្កើត\\!*", keyboard=main_menu_reply_keyboard())


async def _do_vp_with_voice(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    instruction: str,
    ref_bytes: bytes | None,
    voice_id: str = "",
) -> None:
    processing = await context.bot.send_sticker(
        chat_id,
        sticker="CAACAgUAAxkBAAEDu4Zp-rTrlmnphDX-WIT9au-O6aW5CwACLRYAAvgG8VSjN2gKlvlMQTsE",
    )
    result = await generate_speech(
        text=text,
        instruction=_with_khmer_hint(instruction, text),
        reference_audio_bytes=ref_bytes,
        reference_audio_filename="preview.ogg",
    )
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(
        context, chat_id, result, caption="🎭 *សំឡេងបានបង្កើត\\!*",
        keyboard=main_menu_reply_keyboard(),
    )


async def _do_voice_clone(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    ref_bytes: bytes,
    ref_name: str = "ref.ogg",
) -> None:
    processing = await context.bot.send_sticker(
        chat_id,
        sticker="CAACAgUAAxkBAAEDu4Zp-rTrlmnphDX-WIT9au-O6aW5CwACLRYAAvgG8VSjN2gKlvlMQTsE",
    )
    result = await generate_speech(text=text, instruction=_with_khmer_hint("", text), reference_audio_bytes=ref_bytes, reference_audio_filename=ref_name)
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(context, chat_id, result, caption="🎙️ *ក្លូនសំឡេង*", keyboard=main_menu_reply_keyboard())


async def _do_voice_preview(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    voice: dict,
    idx: int = 0,
) -> None:
    voice_id = voice["id"]
    total = len(PRESET_VOICES)
    caption = f"{voice['emoji']} *{_esc(voice['name'])}*"

    # ── 1. Check in-memory cache ──────────────────────────────────────────────
    audio_bytes: bytes | None = context.bot_data.get(f"vp_cache_{voice_id}")

    # ── 2. Check DB cache ─────────────────────────────────────────────────────
    if not audio_bytes:
        audio_bytes = await voice_db.get_cached_voice(voice_id)
        if audio_bytes:
            context.bot_data[f"vp_cache_{voice_id}"] = audio_bytes
            logger.info("Voice preview %s loaded from DB", voice_id)

    context.user_data["vp_current_idx"] = idx
    kb = voice_preview_reply_keyboard(idx)

    # ── 3. Serve immediately if cached ────────────────────────────────────────
    if audio_bytes:
        try:
            ogg_bytes = _to_ogg_opus(audio_bytes)
            voice_file = InputFile(io.BytesIO(ogg_bytes), filename="preview.ogg")
            await context.bot.send_voice(
                chat_id,
                voice=voice_file,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=kb,
            )
        except Exception as exc:
            logger.error("Failed to send cached preview: %s", exc)
        return

    # ── 4. Fallback: generate via API ─────────────────────────────────────────
    processing = await context.bot.send_sticker(
        chat_id,
        sticker="CAACAgUAAxkBAAEDu4Zp-rTrlmnphDX-WIT9au-O6aW5CwACLRYAAvgG8VSjN2gKlvlMQTsE",
    )
    result = await generate_speech(text=voice["sample"], instruction=voice["instruction"])
    await _safe_delete(context, chat_id, processing.message_id)

    if result.get("error") or not result.get("audio_url"):
        err_detail = _esc(str(result.get("error", "Unknown"))[:160])
        await context.bot.send_message(
            chat_id,
            f"❌ *បង្កើតគំរូបានបរាជ័យ*\n\n_{err_detail}_",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=kb,
        )
        return

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            dl = await client.get(result["audio_url"])
            dl.raise_for_status()
            audio_bytes = dl.content

        context.bot_data[f"vp_cache_{voice_id}"] = audio_bytes
        await voice_db.save_cached_voice(voice_id, audio_bytes)

        ogg_bytes = _to_ogg_opus(audio_bytes)
        voice_file = InputFile(io.BytesIO(ogg_bytes), filename="preview.ogg")
        await context.bot.send_voice(
            chat_id,
            voice=voice_file,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=kb,
        )
    except Exception as exc:
        logger.error("Failed to send preview voice: %s", exc)
        await context.bot.send_message(
            chat_id,
            "❌ មិនអាចផ្ញើ voice message បាន\\. សូមព្យាយាមម្ដងទៀត\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=kb,
        )


async def precache_all_voices() -> None:
    """Background task: download and cache all preset voice samples into DB."""
    import asyncio
    logger.info("Starting background voice pre-caching (%d voices)…", len(PRESET_VOICES))
    cached = 0
    for voice in PRESET_VOICES:
        vid = voice["id"]
        existing = await voice_db.get_cached_voice(vid)
        if existing:
            logger.info("Pre-cache: %s already in DB, skipping", vid)
            cached += 1
            continue
        try:
            result = await generate_speech(text=voice["sample"], instruction=voice["instruction"])
            if result.get("error") or not result.get("audio_url"):
                logger.warning("Pre-cache failed for %s: %s", vid, result.get("error"))
                continue
            async with httpx.AsyncClient(timeout=30) as client:
                dl = await client.get(result["audio_url"])
                dl.raise_for_status()
                audio_bytes = dl.content
            await voice_db.save_cached_voice(vid, audio_bytes)
            cached += 1
            logger.info("Pre-cache: saved %s (%d KB) [%d/%d]", vid, len(audio_bytes) // 1024, cached, len(PRESET_VOICES))
            await asyncio.sleep(2)
        except Exception as exc:
            logger.warning("Pre-cache error for %s: %s", vid, exc)
    logger.info("Voice pre-caching complete: %d/%d cached", cached, len(PRESET_VOICES))


def _to_ogg_opus(audio_bytes: bytes) -> bytes:
    """Convert any audio bytes to OGG Opus for Telegram voice messages."""
    tmp_in = tempfile.NamedTemporaryFile(suffix=".audio", delete=False)
    tmp_out_path = tmp_in.name + ".ogg"
    try:
        tmp_in.write(audio_bytes)
        tmp_in.close()
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", tmp_in.name,
                "-c:a", "libopus", "-b:a", "64k",
                tmp_out_path,
            ],
            check=True,
            timeout=30,
        )
        with open(tmp_out_path, "rb") as f:
            return f.read()
    except Exception as exc:
        logger.warning("OGG conversion failed, using raw bytes: %s", exc)
        return audio_bytes
    finally:
        os.unlink(tmp_in.name)
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)


async def _send_audio_result(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    result: dict,
    caption: str,
    keyboard=None,
) -> None:
    if result.get("error") or not result.get("audio_url"):
        err_detail = _esc(str(result.get("error", "Unknown error"))[:180])
        await context.bot.send_message(
            chat_id,
            (
                "❌ *ការបង្កើតបានបរាជ័យ*\n\n"
                f"_{err_detail}_\n\n"
                "សូមសាកល្បង demo ផ្ទាល់: [HuggingFace Space](https://huggingface\\.co/spaces/OpenBMB/VoxCPM\\-Demo)"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        return

    audio_url = result["audio_url"]
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            dl = await client.get(audio_url)
            dl.raise_for_status()
            audio_bytes = dl.content

        ogg_bytes = _to_ogg_opus(audio_bytes)
        voice_file = InputFile(io.BytesIO(ogg_bytes), filename="speech.ogg")
        await context.bot.send_voice(
            chat_id,
            voice=voice_file,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard,
        )
    except Exception as exc:
        logger.error("Failed to send voice: %s", exc)
        await context.bot.send_message(
            chat_id,
            "❌ មិនអាចផ្ញើ voice message បាន\\. សូមព្យាយាមម្ដងទៀត\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard,
        )


async def _safe_delete(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> None:
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception:
        pass
