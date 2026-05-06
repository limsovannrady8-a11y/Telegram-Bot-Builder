from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

BOT_DIR = str(Path(__file__).resolve().parent.parent / "telegram-bot")
if BOT_DIR not in sys.path:
    sys.path.insert(0, BOT_DIR)

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters

from db import init_db
from handlers import on_callback, on_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


def _build_app() -> Application:
    ptb = Application.builder().token(TOKEN).build()
    ptb.add_handler(CallbackQueryHandler(on_callback))
    ptb.add_handler(
        MessageHandler(
            filters.TEXT
            | filters.VOICE
            | filters.AUDIO
            | filters.Document.ALL
            | filters.COMMAND,
            on_message,
        )
    )
    return ptb


async def _process_update(data: dict) -> None:
    ptb = _build_app()
    async with ptb:
        await init_db()
        update = Update.de_json(data, ptb.bot)
        await ptb.process_update(update)


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")

    if method == "GET":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"Webhook active."]

    if method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH", 0) or 0)
            body = environ["wsgi.input"].read(length)
            data = json.loads(body)
            asyncio.run(_process_update(data))
        except Exception as exc:
            logger.error("Webhook error: %s", exc)

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"OK"]
