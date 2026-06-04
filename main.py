import asyncio
import base64
import logging
import subprocess

import aiofiles
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram.types import Message
from vosk import Model

from aibot import aire
from aibot.audio import transcribe_audio
from aibot.config import load_settings
from aibot.photoai import photo_ai


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = load_settings()
settings.voice_dir.mkdir(parents=True, exist_ok=True)
settings.photo_dir.mkdir(parents=True, exist_ok=True)

try:
    speech_model = Model(str(settings.vosk_model_path))
    logger.info("Vosk model loaded from %s", settings.vosk_model_path)
except Exception:
    logger.exception("Could not load Vosk model")
    speech_model = None

bot = Bot(settings.telegram_token)
dp = Dispatcher(storage=MemoryStorage())
users: dict[int, str] = {}


async def send_long_message(message: Message, text: str, parse_mode: str | None = "Markdown") -> None:
    if not text:
        await message.answer("Получился пустой ответ. Напиши еще раз?")
        return

    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)]
    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode=parse_mode)
        except Exception:
            logger.exception("Could not send formatted message, retrying as plain text")
            await message.answer(chunk)


def remember_turn(chat_id: int, user_message: str, bot_response: str) -> None:
    history = users.setdefault(chat_id, "")
    history += f"пользователь: {user_message}\n"
    history += f"майя: {bot_response}\n"
    users[chat_id] = history[-12000:]


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    users[message.chat.id] = ""
    await state.clear()
    await message.answer(
        "Привет! Я Майя. Можно просто написать, что у тебя на душе. "
        "Я не врач, но я рядом и умею слушать без осуждения.",
        parse_mode="HTML",
    )
    logger.info("User started bot: %s", message.chat.id)


@dp.message(F.text)
async def handle_text_message(message: Message, state: FSMContext) -> None:
    users.setdefault(message.chat.id, "")
    try:
        answer = await aire(message, settings.openrouter_key, users, message.text, settings.admin_id)
        await send_long_message(message, answer)
        remember_turn(message.chat.id, message.text, answer)
    except Exception:
        logger.exception("Text message handling failed")
        await message.answer("Что-то пошло не так. Давай попробуем еще раз чуть позже.")


@dp.message(F.voice)
async def handle_voice_message(message: Message) -> None:
    if speech_model is None:
        await message.answer("Сейчас не могу распознать голосовое. Лучше напиши текстом.")
        return

    users.setdefault(message.chat.id, "")
    ogg_path = settings.voice_dir / f"{message.voice.file_id}.ogg"
    wav_path = settings.voice_dir / f"{message.voice.file_id}.wav"

    try:
        file_info = await bot.get_file(message.voice.file_id)
        await bot.download_file(file_info.file_path, destination=ogg_path)

        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(ogg_path), "-ar", "16000", "-ac", "1", str(wav_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError("ffmpeg conversion failed")

        transcribed_text = await transcribe_audio(str(wav_path), speech_model)
        if not transcribed_text.strip():
            await message.answer("Не смогла разобрать голосовое. Можешь написать текстом?")
            return

        answer = await aire(message, settings.openrouter_key, users, transcribed_text, settings.admin_id)
        await send_long_message(message, answer)
        remember_turn(message.chat.id, transcribed_text, answer)
    except Exception:
        logger.exception("Voice message handling failed")
        await message.answer("Не получилось обработать голосовое. Попробуй еще раз или напиши текстом.")
    finally:
        for path in (ogg_path, wav_path):
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                logger.exception("Could not remove temp file: %s", path)


@dp.message(F.photo)
async def handle_photo_message(message: Message, state: FSMContext) -> None:
    users.setdefault(message.chat.id, "")
    photo_path = None

    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        photo_path = settings.photo_dir / f"{message.chat.id}_{photo.file_id}.jpg"
        await bot.download_file(file.file_path, photo_path)

        async with aiofiles.open(photo_path, "rb") as image_file:
            image_bytes = await image_file.read()

        data_url = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
        answer = await photo_ai(data_url, users, message)
        await send_long_message(message, answer)
        remember_turn(message.chat.id, "[изображение]", answer)
    except Exception:
        logger.exception("Photo message handling failed")
        await message.answer("Не получилось обработать изображение. Попробуй отправить другое фото.")
    finally:
        try:
            if photo_path and photo_path.exists():
                photo_path.unlink()
        except OSError:
            logger.exception("Could not remove temp photo: %s", photo_path)


async def main() -> None:
    await bot(DeleteWebhook(drop_pending_updates=True))
    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception:
        logger.exception("Bot crashed")
