import os
from fastapi import Request
from faster_whisper import WhisperModel

def transcribe_audio(file_path: str):

    model_name = os.getenv("STT_MODEL", "small")
    device = os.getenv("STT_DEVICE", "cpu")
   
    stt = WhisperModel(model_name, device=device, compute_type="int8")
    segments, _ = stt.transcribe(file_path, word_timestamps=True, language="ru")

    words = [
        {
            "word": w.word.strip(),
            "start": float(w.start),
            "end": float(w.end),
        }
        for s in segments for w in s.words
    ]

    text = " ".join(w["word"] for w in words)
    return text, words