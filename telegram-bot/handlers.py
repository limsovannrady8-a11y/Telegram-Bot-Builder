import io
import logging
import httpx
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import (
    main_menu_reply_keyboard,
    cancel_reply_keyboard,
    languages_keyboard,
    about_keyboard,
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

WELCOME_TEXT = "🎙️ *សូមស្វាគមន៍មកកាន់ Khmer Text To Voice*"

ABOUT_TEXT = (
    "🧠 *VoxCPM2 — AI TTS កម្រិតខ្ពស់*\n\n"
    "VoxCPM2 គឺជាម៉ូដែលដែលមាន 2B parameters "
    "ហើយត្រូវបានបណ្តុះបណ្តាលលើទិន្នន័យសំឡេងច្រើនជាង *2 លានម៉ោង*\\.\n\n"
    "✨ *មុខងារ:*\n"
    "• 🌍 ៣០ ភាសា \\(រួមមាន ខ្មែរ, ថៃ, ឡាវ, វៀតណាម…\\)\n"
    "• 🎨 រចនាសំឡេង — បង្កើតសំឡេងតាមការពិពណ៌នា\n"
    "• 🎭 មើលសំឡេង — ស្ដាប់គំរូ 12 ប្រភេទសំឡេង\n"
    "• 🎛️ ក្លូនដែលអាចគ្រប់គ្រងបាន — ក្លូនសំឡេងណាមួយ\n"
    "• 🔊 សំឡេងគុណភាព studio 48kHz\n\n"
    "📜 Open\\-source ក្រោម *Apache 2\\.0*"
)

HELP_TEXT = (
    "❓ *របៀបប្រើ VoxCPM Bot:*\n\n"
    "*🗣️ អត្ថបទ → សំឡេង \\(TTS\\)*\n"
    "ផ្ញើអត្ថបទណាមួយ — ទទួលបានសំឡេង voice message ។ គាំទ្រ ៣០ ភាសា \\(auto\\-detected\\)\\!\n\n"
    "*🎭 មើលសំឡេង*\n"
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

    # ── Navigation ──────────────────────────────────────────────────────────
    if data == "menu":
        _clear(context)
        await context.bot.send_message(
            chat_id, WELCOME_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_reply_keyboard(),
        )
        return

    if data == "cancel":
        _clear(context)
        await context.bot.send_message(
            chat_id, "✅ បោះបង់រួចហើយ\\. ត្រឡប់ទៅម៉ឺនុយចម្បង:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_reply_keyboard(),
        )
        return

    # ── Voice Preview — carousel: show voice at index directly ───────────────
    if data.startswith("vp_") and not data.startswith("vp_listen_") and not data.startswith("vp_use_"):
        idx = int(data.split("_")[1])
        if 0 <= idx < len(PRESET_VOICES):
            await _do_voice_preview(context, chat_id, PRESET_VOICES[idx], idx=idx)
        return

    # ── Voice Preview — replay sample ────────────────────────────────────────
    if data.startswith("vp_listen_"):
        voice_id = data[len("vp_listen_"):]
        voice = _find_voice(voice_id)
        if not voice:
            await context.bot.send_message(chat_id, "❌ រកមិនឃើញសំឡេង\\.", parse_mode=ParseMode.MARKDOWN_V2)
            return
        idx = next((i for i, v in enumerate(PRESET_VOICES) if v["id"] == voice_id), 0)
        await _do_voice_preview(context, chat_id, voice, idx=idx)
        return

    # ── Voice Preview — use this voice for custom text ────────────────────────
    if data.startswith("vp_use_"):
        voice_id = data[len("vp_use_"):]
        voice = _find_voice(voice_id)
        if not voice:
            await context.bot.send_message(chat_id, "❌ រកមិនឃើញសំឡេង\\.", parse_mode=ParseMode.MARKDOWN_V2)
            return
        cached_bytes = context.bot_data.get(f"vp_cache_{voice_id}")
        _clear(context)
        context.user_data["instruction"] = voice["instruction"]
        context.user_data["vp_voice_id"] = voice_id
        if cached_bytes:
            context.user_data["vp_ref_bytes"] = cached_bytes
        _set_state(context, STATE_VP_AWAITING_TEXT)
        await context.bot.send_message(
            chat_id,
            (
                f"{voice['emoji']} *{_esc(voice['name'])} — អត្ថបទផ្ទាល់ខ្លួន*\n\n"
                f"ស្ទីលសំឡេង: _{_esc(voice['instruction'][:120])}_\n\n"
                f"ឥឡូវផ្ញើ *អត្ថបទ* ដែលចង់និយាយ:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_reply_keyboard(),
        )
        return

    # ── Languages ─────────────────────────────────────────────────────────────
    if data.startswith("langs_"):
        page = int(data.split("_")[1])
        await context.bot.send_message(
            chat_id,
            "🌍 *ភាសាដែលគាំទ្រ \\(៣០\\)*\n\nVoxCPM2 រកភាសាដោយស្វ័យប្រវត្តិ សម្រាប់ទាំងអស់ខាងក្រោម:",
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
                f"✅ *{_esc(name)}* គាំទ្រហើយ\\!\n\nវាយអត្ថបទជាភាសានោះ ហើយប្រើ *អត្ថបទ → សំឡេង* — VoxCPM2 នឹងរកភាសាដោយស្វ័យប្រវត្តិ\\!",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_reply_keyboard(),
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
    if text == "❌ បោះបង់":
        _clear(context)
        await msg.reply_text(
            "✅ បោះបង់រួចហើយ\\. ត្រឡប់ទៅម៉ឺនុយចម្បង:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_reply_keyboard(),
        )
        return

    if text == "🗣️ អត្ថបទ → សំឡេង":
        _clear(context)
        _set_state(context, STATE_TTS_AWAITING_TEXT)
        await msg.reply_text(
            (
                "🗣️ *ម៉ូដ អត្ថបទ → សំឡេង*\n\n"
                "ផ្ញើអត្ថបទណាមួយ ហើយខ្ញុំនឹងបំប្លែងជា voice message\\."
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
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
                "🎙️ *ម៉ូដ ក្លូនសំឡេង*\n\n"
                "ផ្ញើ *voice message* ឬ *audio file* ជាឯកសារយោង \\(3–30 វិនាទីល្អបំផុត\\)\\.\n\n"
                "VoxCPM2 នឹងក្លូនសំឡេង ហើយនិយាយអត្ថបទណាមួយ ក្នុងស្ទីលនោះ\\.\n\n"
                "📎 ផ្ញើ *audio* យោងរបស់អ្នក:"
            ),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=cancel_reply_keyboard(),
        )
        return

    if text == "🎭 មើលសំឡេង":
        await _do_voice_preview(context, chat_id, PRESET_VOICES[0], idx=0)
        return

    if text == "🌍 ភាសា":
        await msg.reply_text(
            "🌍 *ភាសាដែលគាំទ្រ \\(៣០\\)*\n\nVoxCPM2 រកភាសាដោយស្វ័យប្រវត្តិ សម្រាប់ទាំងអស់ខាងក្រោម:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=languages_keyboard(0),
        )
        return

    if text == "❓ ជំនួយ":
        await msg.reply_text(
            HELP_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=main_menu_reply_keyboard(),
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
                f"✅ Audio យោងទទួលបានហើយ \\({len(audio_bytes) // 1024} KB\\)\\!\n\nឥឡូវផ្ញើ *អត្ថបទ* ដែលចង់និយាយ:",
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


async def _do_tts(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str) -> None:
    short = text[:120] + ("…" if len(text) > 120 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ កំពុងបង្កើតសំឡេង…\n\n_{_esc(short)}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text)
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(
        context, chat_id, result,
        caption="🔊 *VoxCPM2 TTS*",
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
        f"⏳ *កំពុងបង្កើតសំឡេង…*\n\n🎨 _{_esc(short_i)}_\n📝 _{_esc(short_t)}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text, instruction=instruction)
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(context, chat_id, result, caption="🎨 *សំឡេងបានបង្កើត\\!*", keyboard=done_keyboard)


async def _do_vp_with_voice(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    instruction: str,
    ref_bytes: bytes | None,
    voice_id: str = "",
) -> None:
    short_i = instruction[:60] + ("…" if len(instruction) > 60 else "")
    short_t = text[:80] + ("…" if len(text) > 80 else "")
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ *កំពុងបង្កើតសំឡេង…*\n\n🎭 _{_esc(short_i)}_\n📝 _{_esc(short_t)}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(
        text=text,
        instruction=instruction,
        reference_audio_bytes=ref_bytes,
        reference_audio_filename="preview.ogg",
    )
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(
        context, chat_id, result, caption="🎭 *សំឡេងបានបង្កើត\\!*",
        keyboard=use_voice_done_keyboard(voice_id=voice_id),
    )


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
        f"⏳ *កំពុងក្លូនសំឡេង…*\n\n📝 _{_esc(short_t)}_\n\nកំពុង upload audio យោង…",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=text, reference_audio_bytes=ref_bytes, reference_audio_filename=ref_name)
    await _safe_delete(context, chat_id, processing.message_id)
    await _send_audio_result(context, chat_id, result, caption="🎙️ *ក្លូនសំឡេង*")


async def _do_voice_preview(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    voice: dict,
    idx: int = 0,
) -> None:
    processing = await context.bot.send_message(
        chat_id,
        f"⏳ កំពុងបង្កើតគំរូ *{_esc(voice['name'])}*…\n\n_{_esc(voice['instruction'][:100])}_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    result = await generate_speech(text=voice["sample"], instruction=voice["instruction"])
    await _safe_delete(context, chat_id, processing.message_id)

    if result.get("error") or not result.get("audio_url"):
        err_detail = _esc(str(result.get("error", "Unknown"))[:160])
        await context.bot.send_message(
            chat_id,
            f"❌ *បង្កើតគំរូបានបរាជ័យ*\n\n_{err_detail}_",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_voice_preview_keyboard(voice["id"], idx=idx),
        )
        return

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            dl = await client.get(result["audio_url"])
            dl.raise_for_status()
            audio_bytes = dl.content

        # Cache the preview audio so "Use this voice" can use it as reference
        context.bot_data[f"vp_cache_{voice['id']}"] = audio_bytes

        voice_file = InputFile(io.BytesIO(audio_bytes), filename="preview.ogg")
        total = len(PRESET_VOICES)
        caption = (
            f"{voice['emoji']} *{_esc(voice['name'])}* \\({idx + 1}/{total}\\)\n\n"
            f"_{_esc(voice['instruction'][:120])}_"
        )
        await context.bot.send_voice(
            chat_id,
            voice=voice_file,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_voice_preview_keyboard(voice["id"], idx=idx),
        )
    except Exception as exc:
        logger.error("Failed to send preview voice: %s", exc)
        await context.bot.send_message(
            chat_id,
            "❌ មិនអាចផ្ញើ voice message បាន\\. សូមព្យាយាមម្ដងទៀត\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=after_voice_preview_keyboard(voice["id"], idx=idx),
        )


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

        voice_file = InputFile(io.BytesIO(audio_bytes), filename="speech.ogg")
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
