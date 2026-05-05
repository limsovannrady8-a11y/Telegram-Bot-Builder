export const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English 🇬🇧" },
  { code: "km", name: "Khmer 🇰🇭" },
  { code: "zh", name: "Chinese 🇨🇳" },
  { code: "ja", name: "Japanese 🇯🇵" },
  { code: "ko", name: "Korean 🇰🇷" },
  { code: "fr", name: "French 🇫🇷" },
  { code: "de", name: "German 🇩🇪" },
  { code: "es", name: "Spanish 🇪🇸" },
  { code: "hi", name: "Hindi 🇮🇳" },
  { code: "ar", name: "Arabic 🇸🇦" },
  { code: "ru", name: "Russian 🇷🇺" },
  { code: "th", name: "Thai 🇹🇭" },
  { code: "vi", name: "Vietnamese 🇻🇳" },
  { code: "id", name: "Indonesian 🇮🇩" },
  { code: "pt", name: "Portuguese 🇧🇷" },
  { code: "tr", name: "Turkish 🇹🇷" },
  { code: "pl", name: "Polish 🇵🇱" },
  { code: "nl", name: "Dutch 🇳🇱" },
  { code: "it", name: "Italian 🇮🇹" },
  { code: "lo", name: "Lao 🇱🇦" },
];

export const MODES = {
  TTS: "tts",
  VOICE_DESIGN: "voice_design",
  VOICE_CLONE: "voice_clone",
} as const;

export const STEPS = {
  IDLE: "idle",
  AWAITING_TEXT: "awaiting_text",
  AWAITING_INSTRUCTION: "awaiting_instruction",
  AWAITING_INSTRUCTION_THEN_TEXT: "awaiting_instruction_then_text",
  AWAITING_AUDIO: "awaiting_audio",
  AWAITING_AUDIO_TEXT: "awaiting_audio_text",
} as const;

export const CALLBACK = {
  MENU: "menu",
  TTS: "tts",
  VOICE_DESIGN: "vd",
  VOICE_CLONE: "vc",
  LANGUAGES: "langs",
  LANGS_PAGE: "langs_page",
  ABOUT: "about",
  BACK: "back",
  CANCEL: "cancel",
  GENERATE: "generate",
  HELP: "help",
} as const;

export const HF_SPACE_URL = "https://huggingface.co/spaces/OpenBMB/VoxCPM-Demo";
export const GITHUB_URL = "https://github.com/OpenBMB/VoxCPM";
export const HF_MODEL_URL = "https://huggingface.co/openbmb/VoxCPM2";
