SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English 🇬🇧"},
    {"code": "km", "name": "Khmer 🇰🇭"},
    {"code": "zh", "name": "Chinese 🇨🇳"},
    {"code": "ja", "name": "Japanese 🇯🇵"},
    {"code": "ko", "name": "Korean 🇰🇷"},
    {"code": "fr", "name": "French 🇫🇷"},
    {"code": "de", "name": "German 🇩🇪"},
    {"code": "es", "name": "Spanish 🇪🇸"},
    {"code": "hi", "name": "Hindi 🇮🇳"},
    {"code": "ar", "name": "Arabic 🇸🇦"},
    {"code": "ru", "name": "Russian 🇷🇺"},
    {"code": "th", "name": "Thai 🇹🇭"},
    {"code": "vi", "name": "Vietnamese 🇻🇳"},
    {"code": "id", "name": "Indonesian 🇮🇩"},
    {"code": "pt", "name": "Portuguese 🇧🇷"},
    {"code": "tr", "name": "Turkish 🇹🇷"},
    {"code": "pl", "name": "Polish 🇵🇱"},
    {"code": "nl", "name": "Dutch 🇳🇱"},
    {"code": "it", "name": "Italian 🇮🇹"},
    {"code": "lo", "name": "Lao 🇱🇦"},
    {"code": "my", "name": "Burmese 🇲🇲"},
    {"code": "da", "name": "Danish 🇩🇰"},
    {"code": "fi", "name": "Finnish 🇫🇮"},
    {"code": "el", "name": "Greek 🇬🇷"},
    {"code": "he", "name": "Hebrew 🇮🇱"},
    {"code": "ms", "name": "Malay 🇲🇾"},
    {"code": "no", "name": "Norwegian 🇳🇴"},
    {"code": "sv", "name": "Swedish 🇸🇪"},
    {"code": "tl", "name": "Tagalog 🇵🇭"},
    {"code": "sw", "name": "Swahili 🇰🇪"},
]

HF_SPACE_URL = "https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo"
GITHUB_URL = "https://github.com/OpenBMB/VoxCPM"
HF_MODEL_URL = "https://huggingface.co/openbmb/VoxCPM2"
GRADIO_BASE = "https://openbmb-voxcpm-demo.hf.space"

# Conversation states
(
    STATE_IDLE,
    STATE_TTS_AWAITING_TEXT,
    STATE_VD_AWAITING_INSTRUCTION,
    STATE_VD_AWAITING_TEXT,
    STATE_VC_AWAITING_AUDIO,
    STATE_VC_AWAITING_TEXT,
) = range(6)
