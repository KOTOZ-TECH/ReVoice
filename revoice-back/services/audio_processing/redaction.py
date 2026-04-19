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

    audio = ffmpeg.input(input_path)

    filters = []

    for r in ranges:
        try:
            start, end = sorted((float(r[0]), float(r[1])))

            filters.append(
                f"volume=enable='between(t,{start},{end})':volume=0"
            )
        except Exception:
            continue

    if not filters:
        shutil.copy(input_path, output_path)
        return

    audio = audio.filter("volume", "1")
    audio = ffmpeg.filter_(audio, "volume", "1")
    stream = ffmpeg.input(input_path).audio.filter_multi_output("volume","1")

    try:
        (
            ffmpeg
            .output(stream, output_path)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(e.stderr.decode())