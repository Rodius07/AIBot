# AI Bot Maya

Telegram-бот с AI-собеседницей Майей. Бот работает через OpenRouter, принимает текст, голосовые сообщения и фотографии, а также хранит историю диалога для каждого чата.

## Возможности

- Отвечает на текстовые сообщения через модель OpenRouter.
- Использует образ Майи: теплый, спокойный, бережный стиль общения без осуждения.
- Поддерживает историю диалога внутри каждого Telegram-чата.
- Разбивает длинные ответы на части, чтобы они помещались в лимиты Telegram.
- Распознает голосовые сообщения через Vosk после конвертации аудио через `ffmpeg`.
- Анализирует фотографии через мультимодальную модель.
- Берет токены, модели и пути к папкам из файла `keys.env`.

## История чата

История поддерживается для каждого чата отдельно в словаре `users`.

После каждого успешного ответа сохраняется пара сообщений:

```text
пользователь: ...
майя: ...
```

При новом запросе эта история добавляется в system prompt, поэтому бот помнит контекст текущего диалога.

Сейчас история хранится в памяти процесса и ограничивается последними `12000` символами. После перезапуска бота история сбрасывается. Если нужна постоянная история между перезапусками, можно добавить SQLite, Postgres или другое хранилище.

## Модель

Основная модель задается переменной `AI_MODEL`.

Для Gemini 3 Flash через OpenRouter используется:

```env
AI_MODEL=google/gemini-3-flash-preview
VISION_MODEL=google/gemini-3-flash-preview
SEARCH_MODEL=google/gemini-3-flash-preview
```

Адрес OpenRouter API:

```env
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Установка

1. Создать и активировать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Установить зависимости:

```bash
pip install -r requirements.txt
```

3. Установить `ffmpeg`:

```bash
apt install ffmpeg
```

4. Скачать модель Vosk и положить ее в папку `vosk-model-small-ru-0.22`.

Можно указать другой путь через переменную `VOSK_MODEL_PATH`.

5. Создать файл с настройками:

```bash
cp .env.example keys.env
```

6. Заполнить в `keys.env` Telegram token и OpenRouter API key.

## Запуск

```bash
python main.py
```

Бот работает через long polling и при старте сбрасывает старый webhook.

## Переменные окружения

| Переменная | Обязательная | Описание |
| --- | --- | --- |
| `tg_token` | да | Токен Telegram-бота от BotFather |
| `openaitoken` | да | API key OpenRouter |
| `admin_id` | нет | Telegram ID администратора, по умолчанию `991388784` |
| `AI_MODEL` | нет | Основная текстовая модель |
| `VISION_MODEL` | нет | Модель для обработки изображений |
| `SEARCH_MODEL` | нет | Модель для вспомогательных поисковых запросов |
| `OPENROUTER_BASE_URL` | нет | OpenAI-compatible URL OpenRouter |
| `VOICE_DIR` | нет | Папка для временных голосовых файлов |
| `PHOTO_DIR` | нет | Папка для временных фотографий |
| `VOSK_MODEL_PATH` | нет | Путь к локальной модели Vosk |

## Деплой на сервере

Рекомендуется запускать бота через `systemd`, `supervisor`, `pm2`, Docker или другой менеджер процессов.

Пример логики для `systemd`:

```ini
[Unit]
Description=AI Telegram Bot Maya
After=network-online.target

[Service]
WorkingDirectory=/root/AIBot
ExecStart=/root/AIBot/venv/bin/python /root/AIBot/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

После изменения `keys.env` нужно перезапустить процесс бота.

## Проверка

Запустить тесты:

```bash
python -m unittest discover -s tests
```

Проверить синтаксис:

```bash
python -m compileall main.py aibot tests
```

## Безопасность

- Не коммитьте `keys.env`: в нем лежат реальные токены.
- Не загружайте в репозиторий `.idea`, `venv`, `__pycache__`, временные медиафайлы и скачанную модель Vosk.
- Если секрет случайно попал в git-историю, нужно удалить его из истории перед push, иначе GitHub Push Protection заблокирует загрузку.
