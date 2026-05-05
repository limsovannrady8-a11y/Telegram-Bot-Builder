# Workspace

## Overview

pnpm workspace monorepo (Node.js/TypeScript) for the API server, plus a standalone Python Telegram bot.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24 (API server only)
- **Python version**: 3.12 (Telegram bot only)
- **Package manager**: pnpm (Node.js), pip/uv (Python)
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Telegram bot**: python-telegram-bot 21.6 (pure Python, polling mode)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally
- `cd telegram-bot && python bot.py` — run Telegram bot (handled by workflow)

## Telegram Bot (Python)

A pure-Python Telegram bot with inline keyboard buttons integrated with VoxCPM2 TTS AI.

### File structure (`telegram-bot/`)

| File | Purpose |
|---|---|
| `bot.py` | Entry point — builds `Application`, registers handlers, starts polling |
| `handlers.py` | All `CommandHandler`, `CallbackQueryHandler`, `MessageHandler` logic |
| `keyboards.py` | `InlineKeyboardMarkup` builder functions |
| `constants.py` | Shared constants — states, supported languages, URLs |
| `voxcpm_api.py` | Async Gradio API client for HuggingFace Spaces |
| `requirements.txt` | `python-telegram-bot==21.6`, `httpx==0.27.2` |

### Bot features

- `/start` — welcome message with full inline keyboard menu
- `/menu` — return to main menu
- `/help` — usage guide
- 🗣️ **Text-to-Speech** — any text → speech audio (30 languages, auto-detected)
- 🎨 **Voice Design** — describe a voice in words, then speak text with that custom voice
- 🎙️ **Voice Clone** — send reference audio → clone voice → speak any text
- 🌍 **Languages** — paginated inline list of all 30 supported languages
- ℹ️ **About** — links to HuggingFace demo, GitHub repo, model weights

### Conversation state machine

Uses `context.user_data` to track per-user state through multi-step flows:
- `STATE_IDLE` → default
- `STATE_TTS_AWAITING_TEXT` → waiting for text after TTS button
- `STATE_VD_AWAITING_INSTRUCTION` → waiting for voice description
- `STATE_VD_AWAITING_TEXT` → waiting for text after instruction saved
- `STATE_VC_AWAITING_AUDIO` → waiting for reference audio file
- `STATE_VC_AWAITING_TEXT` → waiting for text after audio received

### Environment secrets

- `TELEGRAM_BOT_TOKEN` — required

### VoxCPM source code

- Cloned to `voxcpm-source/` (Python, reference only)
- Live HuggingFace demo: https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo
- Model: https://huggingface.co/openbmb/VoxCPM2

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
