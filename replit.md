# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)
- **Telegram bot**: node-telegram-bot-api (polling mode)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

## Features

### Telegram Bot (VoxCPM Bot)
A Telegram bot with inline keyboard buttons integrated with VoxCPM2 TTS AI.

**Bot file structure:**
- `artifacts/api-server/src/bot/index.ts` — bot entry point (started alongside Express server)
- `artifacts/api-server/src/bot/handlers.ts` — all message and callback_query handlers
- `artifacts/api-server/src/bot/keyboards.ts` — inline keyboard builder functions
- `artifacts/api-server/src/bot/session.ts` — per-user conversation state management
- `artifacts/api-server/src/bot/voxcpm-api.ts` — VoxCPM HuggingFace Spaces API client
- `artifacts/api-server/src/bot/constants.ts` — shared constants (modes, steps, callbacks)

**Bot features:**
- 🗣️ Text-to-Speech — convert any text to speech (30 languages auto-detected)
- 🎨 Voice Design — describe a voice in natural language, then speak text with it
- 🎙️ Voice Clone — send reference audio, clone the voice for any text
- 🌍 Language list with pagination (30 languages including Khmer)
- ℹ️ About + links to HuggingFace demo and GitHub

**Environment secrets:**
- `TELEGRAM_BOT_TOKEN` — required to run the Telegram bot

**VoxCPM source code:**
- Cloned to `voxcpm-source/` (Python, for reference)
- Live HuggingFace demo: https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo
- Model: https://huggingface.co/openbmb/VoxCPM2

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
