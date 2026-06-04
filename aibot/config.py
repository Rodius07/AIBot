import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / "keys.env"


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    openrouter_key: str
    admin_id: int
    model: str
    vision_model: str
    openrouter_base_url: str
    voice_dir: Path
    photo_dir: Path
    vosk_model_path: Path


def load_settings() -> Settings:
    load_dotenv(ENV_PATH)

    telegram_token = os.getenv("tg_token", "").strip()
    openrouter_key = os.getenv("openaitoken", "").strip()
    if not telegram_token:
        raise RuntimeError("tg_token is missing in keys.env")
    if not openrouter_key:
        raise RuntimeError("openaitoken is missing in keys.env")

    return Settings(
        telegram_token=telegram_token,
        openrouter_key=openrouter_key,
        admin_id=int(os.getenv("admin_id", "991388784")),
        model=os.getenv("AI_MODEL", "openrouter/free"),
        vision_model=os.getenv("VISION_MODEL", "openrouter/free"),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        voice_dir=Path(os.getenv("VOICE_DIR", BASE_DIR / "tmp" / "voices")),
        photo_dir=Path(os.getenv("PHOTO_DIR", BASE_DIR / "tmp" / "photos")),
        vosk_model_path=Path(os.getenv("VOSK_MODEL_PATH", BASE_DIR / "vosk-model-small-ru-0.22")),
    )
