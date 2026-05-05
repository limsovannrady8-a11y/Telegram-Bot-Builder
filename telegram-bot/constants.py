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

# ── Preset voice styles for the Voice Preview gallery ──────────────────────
PRESET_VOICES = [
    {
        "id": "tiktok_energetic",
        "emoji": "🔥",
        "name": "TikTok ថាមពល",
        "instruction": "ក្មេងៗ ថាមពលខ្លាំង ស្ទីល TikTok ។ និយាយលឿនៗ ស្រស់ស្រាយ ហ្ស្វ៉ូ ។ ប្រញាប់ ចា ទាក់ទាញ ដូចវីឌីអូ TikTok ដែលល្បីៗ ។",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "news_reporter",
        "emoji": "📺",
        "name": "អ្នករាយការណ៍ព័ត៌មាន",
        "instruction": "A professional TV news reporter with a clear, authoritative, and neutral voice. Steady confident pace, crisp pronunciation, serious and credible tone — like a prime-time broadcast anchor.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "calm_narration",
        "emoji": "🌙",
        "name": "ការរៀបរាប់ស្ងប់ស្ងាត់",
        "instruction": "A deeply calm and soothing narrator. Slow, smooth, and peaceful tone — like a bedtime story or documentary voice-over. Every word is gentle and unhurried, creating a relaxing atmosphere.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "funny_khmer",
        "emoji": "😀",
        "name": "កំប្លែងខ្មែរ",
        "instruction": "A funny, playful Khmer comedian voice. Speaks with a light-hearted, humorous and exaggerated tone, full of personality and local Khmer charm. Slightly dramatic pauses for comedic effect.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "professional_ad",
        "emoji": "💼",
        "name": "ផ្សាយពាណិជ្ជកម្ម",
        "instruction": "A polished, confident advertising voice. Warm yet authoritative, smooth and persuasive — like a high-budget TV commercial. Speaks clearly with controlled enthusiasm, inspiring trust and desire in the listener.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "gentle_woman",
        "emoji": "👩",
        "name": "ស្ត្រីទន់ភ្លន់",
        "instruction": "A young woman with a soft, warm voice. Speaks slowly and gently with a calming, nurturing tone.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "deep_narrator",
        "emoji": "🎙️",
        "name": "អ្នករៀបរាប់ជ្រៅ",
        "instruction": "A deep, rich male voice with a dramatic, authoritative tone. Speaks clearly and powerfully, like a movie trailer narrator.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "wise_elder",
        "emoji": "🧓",
        "name": "ចាស់ទុំប្រាជ្ញ",
        "instruction": "An elderly person with a wise, warm voice. Speaks slowly and thoughtfully, with calm authority and years of experience.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "cheerful_host",
        "emoji": "😄",
        "name": "អ្នកនាំបង្ហាញរីករាយ",
        "instruction": "A cheerful, friendly TV show host with a bright, bubbly voice. Warm, inviting, and always smiling through their words.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "dramatic_actor",
        "emoji": "🎭",
        "name": "តួអូសខ្លាំង",
        "instruction": "A theatrical, expressive actor with a dramatic voice full of emotion. Rich tones, deliberate pauses, intense delivery.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "sweet_child",
        "emoji": "🧒",
        "name": "កូនតូចស្រណោះ",
        "instruction": "A young child's voice, sweet and innocent, slightly high-pitched. Speaks cheerfully and simply, with pure curiosity.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
    {
        "id": "robot",
        "emoji": "🤖",
        "name": "រ៉ូបូត / AI",
        "instruction": "A robotic, synthetic AI voice. Flat, monotone, precise. Speaks without emotion, perfectly measured pace.",
        "sample": "ជម្រាបសួរអ្នកទាំងអស់គ្នា សូមស្វាគមន៍មកកាន់ លឹម សុវណ្ណរ៉ាឌី Bot",
    },
]

HF_SPACE_URL = "https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo"
GITHUB_URL = "https://github.com/OpenBMB/VoxCPM"
HF_MODEL_URL = "https://huggingface.co/openbmb/VoxCPM2"
GRADIO_BASE = "https://openbmb-voxcpm-demo.hf.space"

VOICES_PER_PAGE = 6

# Conversation states
(
    STATE_IDLE,
    STATE_TTS_AWAITING_TEXT,
    STATE_VD_AWAITING_INSTRUCTION,
    STATE_VD_AWAITING_TEXT,
    STATE_VC_AWAITING_AUDIO,
    STATE_VC_AWAITING_TEXT,
    STATE_VP_AWAITING_TEXT,
) = range(7)
