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
        "id": "gentle_woman",
        "emoji": "👩",
        "name": "Gentle Woman",
        "instruction": "A young woman with a soft, warm voice. Speaks slowly and gently with a calming, nurturing tone.",
        "sample": "Hello! I hope you're having a wonderful day. I'm here to help you with anything you need.",
    },
    {
        "id": "deep_narrator",
        "emoji": "🎙️",
        "name": "Deep Narrator",
        "instruction": "A deep, rich male voice with a dramatic, authoritative tone. Speaks clearly and powerfully, like a movie trailer narrator.",
        "sample": "In a world where anything is possible, one voice rises above all others to tell the story.",
    },
    {
        "id": "energetic_teen",
        "emoji": "⚡",
        "name": "Energetic Teen",
        "instruction": "An energetic teenager with an upbeat, enthusiastic voice. Speaks fast and excitedly, full of life and energy.",
        "sample": "Oh my gosh, this is literally the best thing ever! I can't believe how amazing this is!",
    },
    {
        "id": "wise_elder",
        "emoji": "🧓",
        "name": "Wise Elder",
        "instruction": "An elderly person with a wise, warm voice. Speaks slowly and thoughtfully, with calm authority and years of experience.",
        "sample": "In my many years, I have learned that patience and kindness are the greatest gifts we can offer.",
    },
    {
        "id": "news_anchor",
        "emoji": "📰",
        "name": "News Anchor",
        "instruction": "A professional news anchor with a clear, neutral, and confident voice. Crisp pronunciation, steady pace, authoritative tone.",
        "sample": "Good evening. Tonight's top stories: scientists have made a breakthrough discovery that could change the world.",
    },
    {
        "id": "melancholic_girl",
        "emoji": "🌧️",
        "name": "Melancholic Girl",
        "instruction": "A young girl with a soft, sweet voice. Speaks slowly with a melancholic, slightly sad tone, as if holding back tears.",
        "sample": "I never asked you to stay. It's not like I care or anything. But why does it still hurt so much?",
    },
    {
        "id": "cheerful_host",
        "emoji": "😄",
        "name": "Cheerful Host",
        "instruction": "A cheerful, friendly TV show host with a bright, bubbly voice. Warm, inviting, and always smiling through their words.",
        "sample": "Welcome, welcome, welcome everyone! We have an absolutely fantastic show lined up for you today!",
    },
    {
        "id": "calm_meditation",
        "emoji": "🧘",
        "name": "Calm Meditation",
        "instruction": "An extremely calm and peaceful voice, soft and slow, like a meditation guide. Soothing, gentle breathing rhythm in speech.",
        "sample": "Take a deep breath. Relax your shoulders. Feel the tension melt away as you breathe out slowly.",
    },
    {
        "id": "dramatic_actor",
        "emoji": "🎭",
        "name": "Dramatic Actor",
        "instruction": "A theatrical, expressive actor with a dramatic voice full of emotion. Rich tones, deliberate pauses, intense delivery.",
        "sample": "To be, or not to be — that is the question. Whether 'tis nobler in the mind to suffer...",
    },
    {
        "id": "sweet_child",
        "emoji": "🧒",
        "name": "Sweet Child",
        "instruction": "A young child's voice, sweet and innocent, slightly high-pitched. Speaks cheerfully and simply, with pure curiosity.",
        "sample": "Look, look! I found a butterfly! It's so pretty and it has yellow wings! Can we keep it?",
    },
    {
        "id": "villain",
        "emoji": "😈",
        "name": "Sinister Villain",
        "instruction": "A dark, menacing villain voice. Low, slow, and dangerous. Every word drips with cold confidence and quiet threat.",
        "sample": "You thought you could escape me? How delightfully naive. Everything is going exactly according to my plan.",
    },
    {
        "id": "robot",
        "emoji": "🤖",
        "name": "Robot / AI",
        "instruction": "A robotic, synthetic AI voice. Flat, monotone, precise. Speaks without emotion, perfectly measured pace.",
        "sample": "Hello human. I have processed your request. Generating optimal response. All systems are operational.",
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
