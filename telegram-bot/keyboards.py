from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from constants import SUPPORTED_LANGUAGES, PRESET_VOICES, VOICES_PER_PAGE

LANGS_PER_PAGE = 6


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🗣️ អត្ថបទ → សំឡេង", callback_data="tts"),
            InlineKeyboardButton("🎨 រចនាសំឡេង", callback_data="vd"),
        ],
        [
            InlineKeyboardButton("🎙️ ក្លូនសំឡេង", callback_data="vc"),
            InlineKeyboardButton("🎭 មើលសំឡេង", callback_data="vp_0"),
        ],
        [
            InlineKeyboardButton("🌍 ភាសា", callback_data="langs_0"),
            InlineKeyboardButton("❓ ជំនួយ", callback_data="help"),
        ],
    ])


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ បោះបង់", callback_data="cancel")],
    ])


def back_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ បោះបង់", callback_data="cancel"),
            InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu"),
        ],
    ])


def after_generate_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 បង្កើតម្ដងទៀត", callback_data="tts"),
            InlineKeyboardButton("🎭 មើលសំឡេង", callback_data="vp_0"),
        ],
        [InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu")],
    ])


def voice_preview_list_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    start = page * VOICES_PER_PAGE
    slice_ = PRESET_VOICES[start: start + VOICES_PER_PAGE]

    rows = []
    for v in slice_:
        rows.append([
            InlineKeyboardButton(
                f"{v['emoji']} {v['name']}",
                callback_data=f"vp_listen_{v['id']}",
            )
        ])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("◀️ មុន", callback_data=f"vp_{page - 1}"))
    if start + VOICES_PER_PAGE < len(PRESET_VOICES):
        nav_row.append(InlineKeyboardButton("បន្ទាប់ ▶️", callback_data=f"vp_{page + 1}"))
    if nav_row:
        rows.append(nav_row)

    rows.append([InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def after_voice_preview_keyboard(voice_id: str, page: int = 0) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ ប្រើសំឡេងនេះ", callback_data=f"vp_use_{voice_id}"),
            InlineKeyboardButton("🔄 ស្ដាប់ម្ដងទៀត", callback_data=f"vp_listen_{voice_id}"),
        ],
        [InlineKeyboardButton("◀️ ត្រឡប់ទៅបញ្ជីសំឡេង", callback_data=f"vp_{page}")],
        [InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu")],
    ])


def use_voice_done_keyboard(voice_id: str = "", page: int = 0) -> InlineKeyboardMarkup:
    regen_data = f"vp_use_{voice_id}" if voice_id else "tts"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 អត្ថបទថ្មី — សំឡេងដូចគ្នា", callback_data=regen_data),
            InlineKeyboardButton("🎭 សំឡេងបន្ថែម", callback_data=f"vp_{page}"),
        ],
        [InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu")],
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
        nav_row.append(InlineKeyboardButton("◀️ មុន", callback_data=f"langs_{page - 1}"))
    if start + LANGS_PER_PAGE < len(SUPPORTED_LANGUAGES):
        nav_row.append(InlineKeyboardButton("បន្ទាប់ ▶️", callback_data=f"langs_{page + 1}"))
    if nav_row:
        rows.append(nav_row)

    rows.append([InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def about_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤗 HuggingFace Demo", url="https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo")],
        [
            InlineKeyboardButton("📦 GitHub Repo", url="https://github.com/OpenBMB/VoxCPM"),
            InlineKeyboardButton("🧠 Model Weights", url="https://huggingface.co/openbmb/VoxCPM2"),
        ],
        [InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu")],
    ])
