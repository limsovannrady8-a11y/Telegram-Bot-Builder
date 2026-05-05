import logging
import os
import sys

from telegram import BotCommand
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers import cmd_start, cmd_help, cmd_menu, on_callback, on_message

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start", "Start the bot / show main menu"),
        BotCommand("menu", "Show main menu"),
        BotCommand("help", "How to use VoxCPM Bot"),
    ])
    me = await application.bot.get_me()
    logger.info("Bot started: @%s", me.username)


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

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(
        MessageHandler(
            filters.TEXT | filters.VOICE | filters.AUDIO | filters.Document.ALL,
            on_message,
        )
    )

    logger.info("Starting polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
