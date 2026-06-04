from openai import OpenAI

from aibot.config import load_settings


settings = load_settings()
client = OpenAI(base_url=settings.openrouter_base_url, api_key=settings.openrouter_key)


def search_web_gpt(query):
    completion = client.chat.completions.create(
        model=settings.search_model,
        messages=[
            {"role": "system", "content": "Верни краткий результат поиска по запросу."},
            {"role": "user", "content": query},
        ],
        max_tokens=1000,
    )
    return completion.choices[0].message.content
