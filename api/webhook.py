import asyncio
import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Resolve telegram-bot path relative to this file, regardless of cwd
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
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(
        MessageHandler(
            filters.TEXT
            | filters.VOICE
            | filters.AUDIO
            | filters.Document.ALL
            | filters.COMMAND,
            on_message,
        )
    )
    return app


async def _process_update(data: dict) -> None:
    app = _build_app()
    async with app:
        await init_db()
        update = Update.de_json(data, app.bot)
        await app.process_update(update)


class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(format, *args)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            asyncio.run(_process_update(data))
        except Exception as exc:
            logger.error("Webhook error: %s", exc)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Webhook active.")
