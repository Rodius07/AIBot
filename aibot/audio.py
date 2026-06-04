import json
import wave
from vosk import KaldiRecognizer


async def transcribe_audio(wav_path: str,model) -> str:
    rec = KaldiRecognizer(model, 16000)

    with wave.open(wav_path, "rb") as wf:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

    result = json.loads(rec.FinalResult())
    return result.get("text", "")