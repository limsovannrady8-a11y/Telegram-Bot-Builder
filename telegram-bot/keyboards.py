from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from constants import SUPPORTED_LANGUAGES, PRESET_VOICES, VOICES_PER_PAGE

LANGS_PER_PAGE = 6

BTN_TTS  = "🗣️ អត្ថបទ → សំឡេង"
BTN_VD   = "🎨 រចនាសំឡេង"
BTN_VC   = "🎙️ ក្លូនសំឡេង"
BTN_VP   = "🎭 មើលសំឡេង"
BTN_CANCEL = "❌ បោះបង់"


def main_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [BTN_TTS, BTN_VD],
            [BTN_VC,  BTN_VP],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )


def cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[BTN_CANCEL]],
        resize_keyboard=True,
        is_persistent=True,
    )


def after_voice_preview_keyboard(voice_id: str, idx: int = 0) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("✏️ ប្រើសំឡេងនេះ", callback_data=f"vp_use_{voice_id}"),
            InlineKeyboardButton("🔄 ស្ដាប់ម្ដងទៀត", callback_data=f"vp_listen_{voice_id}"),
        ],
    ]
    nav_row = []
    if idx > 0:
        prev_v = PRESET_VOICES[idx - 1]
        nav_row.append(InlineKeyboardButton(
            f"◀️ {prev_v['emoji']} {prev_v['name']}", callback_data=f"vp_{idx - 1}"
        ))
    if idx < len(PRESET_VOICES) - 1:
        next_v = PRESET_VOICES[idx + 1]
        nav_row.append(InlineKeyboardButton(
            f"{next_v['emoji']} {next_v['name']} ▶️", callback_data=f"vp_{idx + 1}"
        ))
    if nav_row:
        rows.append(nav_row)
    rows.append([InlineKeyboardButton("🏠 ម៉ឺនុយចម្បង", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def use_voice_done_keyboard(voice_id: str = "", page: int = 0) -> InlineKeyboardMarkup:
    regen_data = f"vp_use_{voice_id}" if voice_id else "vp_0"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 អត្ថបទថ្មី — សំឡេងដូចគ្នា", callback_data=regen_data),
            InlineKeyboardButton("🎭 សំឡេងបន្ថែម", callback_data=f"vp_{page}"),
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
