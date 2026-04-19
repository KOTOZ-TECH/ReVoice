import os
import re
from pathlib import Path

from services.audio_processing.redaction import apply_redaction
from services.audio_processing.llm import process_to_llm
from services.audio_processing.transcribe import transcribe_audio


BASE_STORAGE = Path("storage")
EDIT_DIR = BASE_STORAGE / "edit"
EDIT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_ranges(raw):
    """Приводит ranges к виду [[float, float], ...]"""
    result = []

    for item in raw:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            try:
                result.append([float(item[0]), float(item[1])])
            except (ValueError, TypeError):
                continue

        elif isinstance(item, str):
            parts = re.findall(r'[\d.]+', item)
            if len(parts) >= 2:
                try:
                    result.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    continue

    return result


def build_output_path(file_path: str) -> Path:
    filename = f"redacted_{Path(file_path).name}"
    return EDIT_DIR / filename


def build_response(raw_text, redacted_text, ranges, output_path: Path):
    return {
        "original_text": raw_text,
        "redacted_text": redacted_text,
        "edit_url": output_path.name,
        "red_zones": [
            {
                "start": float(r[0]),
                "width": float(r[1] - r[0]),
            }
            for r in ranges
        ],
    }


def load_prompt() -> str:
    path = Path(os.getenv("LLM_PROMPT", "core/system_prompt.txt"))

    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    return path.read_text(encoding="utf-8")


def process_audio(file_path: str):
    # Делаем транскрипцию аудио файла
    raw_text, words_data = transcribe_audio(file_path)
    # Загружаем инструкции для LLM
    SYSTEM_PROMPT = load_prompt()
    # Обработка LLM
    try:
        result = process_to_llm(raw_text, words_data, SYSTEM_PROMPT)

        formatted = result.get("formatted_text", raw_text)
        redacted_text = formatted.replace("[[", "<d>").replace("]]", "</d>")
        ranges = normalize_ranges(result.get("ranges", []))

    except Exception as e:
        print(f"LLM error: {e}")
        redacted_text = raw_text
        ranges = []

    # Редактируем аудио файл
    output_path = build_output_path(file_path)
    apply_redaction(file_path, ranges, output_path)

    # Отдаём ответ пользователю
    return build_response(raw_text, redacted_text, ranges, output_path)