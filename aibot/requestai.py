import asyncio

from openai import OpenAI

from aibot.config import load_settings
from aibot.prompts import build_messages


settings = load_settings()
client = OpenAI(base_url=settings.openrouter_base_url, api_key=settings.openrouter_key)


async def aire(message, ai_key, users, txt, admin_id, tmp=""):
    history = users.get(message.chat.id, "")
    completion = await asyncio.to_thread(
        client.chat.completions.create,
        model=settings.model,
        messages=build_messages(history, txt),
        max_tokens=1200,
    )
    return completion.choices[0].message.content or "Я рядом, но сейчас не смогла подобрать ответ. Попробуй написать еще раз."
