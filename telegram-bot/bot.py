import asyncio
import logging
import os
import sys

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from db import init_db
from handlers import on_callback, on_message, precache_all_voices

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.delete_my_commands()
    me = await application.bot.get_me()
    logger.info("Bot started: @%s", me.username)
    await init_db()
    asyncio.create_task(precache_all_voices())


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set.")
        sys.exit(1)

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.VOICE | filters.AUDIO | filters.Document.ALL | filters.COMMAND,
            on_message,
        )
    )

    logger.info("Starting polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
