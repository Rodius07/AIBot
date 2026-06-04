import asyncio

from openai import OpenAI

from aibot.config import load_settings


settings = load_settings()
client = OpenAI(base_url=settings.openrouter_base_url, api_key=settings.openrouter_key)


async def photo_ai(url, users, message):
    response = await asyncio.to_thread(
        client.chat.completions.create,
        model=settings.vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": url},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"История переписки:\n{users.get(message.chat.id, '')}\n\n"
                            "Ответь тепло и по-человечески. Если на фото есть чувствительная тема "
                            "здоровья, еды или тела, не оценивай внешность и не давай медицинских советов. "
                            "Ответ должен быть не больше 4096 символов."
                        ),
                    },
                ],
            }
        ],
        max_tokens=1200,
    )
    return response.choices[0].message.content
