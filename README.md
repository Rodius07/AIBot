# AI Bot Maya

Telegram bot with an OpenRouter-powered AI companion named Maya. The bot supports text messages, voice messages through Vosk speech recognition, and photo analysis through a multimodal model.

## What It Does

- Keeps a per-chat dialogue history in memory and sends it to the model with every new message.
- Answers with the Maya support prompt: warm, careful, non-judgmental, and safe around eating disorder, weight, health, self-harm, and medical topics.
- Splits long replies into Telegram-safe chunks.
- Transcribes Telegram voice messages with Vosk after converting audio through `ffmpeg`.
- Sends photos to the configured vision model and includes the current chat history in the photo prompt.
- Loads tokens, model names, directories, and API base URL from `keys.env`.

## Chat History

History is supported per Telegram chat in the `users` dictionary. Every successful user/bot turn is appended as:

```text
пользователь: ...
майя: ...
```

The active context is trimmed to the latest 12,000 characters to keep requests manageable. This history is in memory, so it resets when the bot process restarts. If persistent history is needed later, add a small database such as SQLite or Postgres.

## Model

The default model is configured through `AI_MODEL`. For Gemini 3 Flash on OpenRouter, use:

```env
AI_MODEL=google/gemini-3-flash-preview
VISION_MODEL=google/gemini-3-flash-preview
SEARCH_MODEL=google/gemini-3-flash-preview
```

OpenRouter endpoint:

```env
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install `ffmpeg`:

```bash
apt install ffmpeg
```

4. Download a Vosk model and place it at `vosk-model-small-ru-0.22`, or set `VOSK_MODEL_PATH` in `keys.env`.

5. Create `keys.env` from the example:

```bash
cp .env.example keys.env
```

6. Fill in `tg_token` and `openaitoken`.

## Running

```bash
python main.py
```

The bot uses long polling and drops pending webhook updates on startup.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `tg_token` | yes | Telegram bot token from BotFather |
| `openaitoken` | yes | OpenRouter API key |
| `admin_id` | no | Telegram admin id, defaults to `991388784` |
| `AI_MODEL` | no | Text model, defaults to `openrouter/free` |
| `VISION_MODEL` | no | Vision model, defaults to `openrouter/free` |
| `SEARCH_MODEL` | no | Search/helper model, defaults to `openrouter/free` |
| `OPENROUTER_BASE_URL` | no | OpenRouter OpenAI-compatible API URL |
| `VOICE_DIR` | no | Temporary directory for voice files |
| `PHOTO_DIR` | no | Temporary directory for photo files |
| `VOSK_MODEL_PATH` | no | Path to the local Vosk model |

## Deployment Notes

- Do not commit `keys.env`; it contains live Telegram and OpenRouter tokens.
- Keep `venv`, `__pycache__`, `.idea`, temporary media files, and downloaded Vosk models out of git.
- Use a process manager such as `systemd`, `pm2`, `supervisor`, or Docker to keep the bot running on a server.
- Restart the process after changing `keys.env`.

## Quick Check

Run the lightweight tests:

```bash
python -m unittest discover -s tests
```

Run a syntax check:

```bash
python -m compileall main.py aibot tests
```
