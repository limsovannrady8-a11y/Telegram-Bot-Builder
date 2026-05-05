# Workspace

## Overview

Standalone Python Telegram bot integrated with VoxCPM2 TTS AI.

## Stack

- **Python version**: 3.12
- **Package manager**: pip / uv
- **Telegram bot**: python-telegram-bot 21.6 (polling mode)
- **Database**: PostgreSQL (Neon) via asyncpg — voice cache

## Key Commands

- `cd telegram-bot && python bot.py` — run Telegram bot (handled by workflow)

## Telegram Bot (Python)

A pure-Python Telegram bot with reply keyboard buttons integrated with VoxCPM2 TTS AI.

### File structure (`telegram-bot/`)

| File | Purpose |
|---|---|
| `bot.py` | Entry point — builds `Application`, registers handlers, starts polling |
| `handlers.py` | All `CallbackQueryHandler`, `MessageHandler` logic |
| `keyboards.py` | `ReplyKeyboardMarkup` builder functions |
| `constants.py` | Shared constants — states, supported languages, preset voices |
| `voxcpm_api.py` | Async Gradio API client for HuggingFace Spaces |
| `db.py` | asyncpg voice cache (PostgreSQL/Neon) |
| `requirements.txt` | `python-telegram-bot==21.6`, `httpx==0.27.2` |

### Bot features

- **📝 អត្ថបទ → សំឡេង** — any text → speech audio (30 languages, Khmer auto-enhanced)
- **🎨 រចនាសំឡេង** — describe a voice, then speak text with that custom voice
- **🎙️ ក្លូនសំឡេង** — send reference audio → clone voice → speak any text
- **🔊 ជ្រើសរើសសំឡេង** — paginated list of 12 preset voices with Khmer names

### Conversation state machine

Uses `context.user_data` to track per-user state:
- `STATE_IDLE` → default
- `STATE_TTS_AWAITING_TEXT` → waiting for text after TTS button
- `STATE_VD_AWAITING_INSTRUCTION` → waiting for voice description
- `STATE_VD_AWAITING_TEXT` → waiting for text after instruction saved
- `STATE_VC_AWAITING_AUDIO` → waiting for reference audio file
- `STATE_VC_AWAITING_TEXT` → waiting for text after audio received
- `STATE_VP_AWAITING_TEXT` → waiting for text after preset voice selected

### Khmer language support

Automatically detects Khmer text (Unicode U+1780–U+17FF, >15% threshold) and injects a Khmer pronunciation instruction into VoxCPM2 for all TTS flows.

### Environment secrets

- `TELEGRAM_BOT_TOKEN` — required
- `NEON_DATABASE_URL` — required (voice cache DB)
