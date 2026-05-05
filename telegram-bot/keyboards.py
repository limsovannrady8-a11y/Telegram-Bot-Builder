from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from constants import SUPPORTED_LANGUAGES

LANGS_PER_PAGE = 6


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗣️ Text-to-Speech", callback_data="tts"),
            InlineKeyboardButton("🎨 Voice Design", callback_data="vd"),
        ],
        [
            InlineKeyboardButton("🎙️ Voice Clone", callback_data="vc"),
            InlineKeyboardButton("🌍 Languages", callback_data="langs_0"),
        ],
        [
            InlineKeyboardButton("ℹ️ About VoxCPM", callback_data="about"),
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
    ])


def back_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="menu"),
        ],
    ])


def after_generate_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Generate Another", callback_data="tts"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="menu"),
        ],
    ])


def languages_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    start = page * LANGS_PER_PAGE
    slice_ = SUPPORTED_LANGUAGES[start: start + LANGS_PER_PAGE]

    rows = []
    for i in range(0, len(slice_), 2):
        row = [InlineKeyboardButton(slice_[i]["name"], callback_data=f"lang_{slice_[i]['code']}")]
        if i + 1 < len(slice_):
            row.append(InlineKeyboardButton(slice_[i + 1]["name"], callback_data=f"lang_{slice_[i + 1]['code']}"))
        rows.append(row)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀️ Prev", callback_data=f"langs_{page - 1}"))
    if start + LANGS_PER_PAGE < len(SUPPORTED_LANGUAGES):
        nav_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"langs_{page + 1}"))
    if nav_row:
        rows.append(nav_row)

    rows.append([InlineKeyboardButton("🏠 Main Menu", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def about_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤗 HuggingFace Demo", url="https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo")],
        [
            InlineKeyboardButton("📦 GitHub Repo", url="https://github.com/OpenBMB/VoxCPM"),
            InlineKeyboardButton("🧠 Model Weights", url="https://huggingface.co/openbmb/VoxCPM2"),
        ],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="menu")],
    ])
