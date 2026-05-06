# VoxCPM2 Telegram TTS Bot

A Python Telegram bot that converts text to speech using VoxCPM2 AI (HuggingFace Spaces), with support for 30 languages, voice cloning, and voice design.

## Run & Operate

- **Run bot**: `cd telegram-bot && python bot.py` (handled by the "Telegram Bot (Python)" workflow)
- **Required secrets**: `TELEGRAM_BOT_TOKEN`, `NEON_DATABASE_URL`

## Stack

- Python 3.12
- python-telegram-bot 21.6 (polling mode)
- asyncpg — PostgreSQL async client for voice cache
- httpx 0.27.2 — HTTP client for VoxCPM2 Gradio API calls
- gradio-client 1.3.0 — Gradio API client
- PostgreSQL (Neon) — voice cache database

## Where things live

- `telegram-bot/` — all bot source code
  - `bot.py` — entry point, registers handlers, starts polling
  - `handlers.py` — all message and callback handler logic
  - `keyboards.py` — ReplyKeyboardMarkup builder functions
  - `constants.py` — states, supported languages, preset voices
  - `voxcpm_api.py` — async Gradio API client for HuggingFace VoxCPM2 Space
  - `db.py` — asyncpg voice cache (PostgreSQL/Neon)
- `voxcpm-source/` — upstream VoxCPM2 model source (reference only, not used at runtime)

## Architecture decisions

- Bot runs in polling mode (not webhook) — simpler for long-running Replit deployments
- Voice cache stored in Neon PostgreSQL as BYTEA to avoid re-generating common preset voices
- VoxCPM2 is consumed as a hosted HuggingFace Gradio API (no local model inference)
- Khmer language auto-detected via Unicode range U+1780–U+17FF (>15% threshold) and injected as a control instruction
- All secrets stored in Replit Secrets (not env vars) for security

## Product

- **Text → Speech**: any text in 30 languages converted to audio
- **Voice Design**: describe a voice in natural language, then speak with it
- **Voice Cloning**: send a reference audio clip → clone that voice → TTS
- **Preset Voices**: 12+ named preset voices (paginated), pre-cached in DB for speed

## User preferences

- Bot is Khmer-language focused (UI labels in Khmer)

## Gotchas

- `NEON_DATABASE_URL` must be a secret (not a plain env var) — the bot uses it via `os.environ.get()`
- The VoxCPM2 HuggingFace Space (`openbmb-voxcpm-demo.hf.space`) must be publicly accessible
- Voice cache table is auto-created on first run via `init_db()`

## Pointers

- VoxCPM2 Gradio Space: https://huggingface.co/spaces/openbmb/VoxCPM-demo
- python-telegram-bot docs: https://python-telegram-bot.org/
