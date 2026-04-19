import shutil
from pathlib import Path
import ffmpeg

def apply_redaction(input_path: str, ranges: list, output_path: str):
    input_path = str(Path(input_path).resolve())
    output_path = str(Path(output_path).resolve())
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not ranges:
        shutil.copy(input_path, output_path)
        return

    filter_parts = []
    for r in ranges:
        try:
            start, end = sorted((float(r[0]), float(r[1])))
            filter_parts.append(f"volume=enable='between(t,{start},{end})':volume=0")
        except Exception:
            continue

    if not filter_parts:
        shutil.copy(input_path, output_path)
        return

    filter_chain = ",".join(filter_parts)

    stream = ffmpeg.input(input_path).audio.filter("aeval", "0", enable=None)  # placeholder
    audio = ffmpeg.input(input_path).audio
    for r in ranges:
        try:
            start, end = sorted((float(r[0]), float(r[1])))
            audio = audio.filter("volume", enable=f"between(t,{start},{end})", volume=0)
        except Exception:
            continue

    try:
        (
            ffmpeg
            .output(audio, output_path)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(e.stderr.decode())