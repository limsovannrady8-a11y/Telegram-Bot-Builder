from telegram import ReplyKeyboardMarkup
from constants import PRESET_VOICES

BTN_TTS    = "📝 អត្ថបទ → សំឡេង"
BTN_VD     = "🎨 រចនាសំឡេង"
BTN_VC     = "🎙️ ក្លូនសំឡេង"
BTN_VP     = "🔊 ជ្រើសរើសសំឡេង"
BTN_RV     = "🎲 Random Voice"
BTN_CANCEL = "⬅️"


def main_menu_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [BTN_TTS, BTN_VD],
            [BTN_VC,  BTN_VP],
            [BTN_RV],
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


def voice_list_reply_keyboard() -> ReplyKeyboardMarkup:
    rows = []
    for i in range(0, len(PRESET_VOICES), 2):
        row = [f"{PRESET_VOICES[i]['emoji']} {PRESET_VOICES[i]['name']}"]
        if i + 1 < len(PRESET_VOICES):
            row.append(f"{PRESET_VOICES[i + 1]['emoji']} {PRESET_VOICES[i + 1]['name']}")
        rows.append(row)
    rows.append([BTN_CANCEL])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def voice_preview_reply_keyboard(idx: int) -> ReplyKeyboardMarkup:
    rows = []
    rows.append(["✏️ ប្រើសំឡេងនេះ"])
    rows.append([BTN_CANCEL])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)
