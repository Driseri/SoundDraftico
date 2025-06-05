"""
 transcriber.py – переиспользуемый модуль для транскрибации аудио через Faster‑Whisper
 с выводом прогресса в консоль.

 Использование из кода::

    from transcriber import transcribe_audio
    text_file = transcribe_audio("/path/audio.m4a")

 Использование из CLI::

     python -m transcriber path/to/audio.wav --model large-v3 --device cuda


 """

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Optional, Union
from tqdm import tqdm

# ``TranscriptionProgress`` was introduced in later versions of
# ``faster_whisper``.  Older releases expose only ``WhisperModel`` and do not
# provide structured progress callbacks.  To keep compatibility with both the
# old and the new versions we try to import ``TranscriptionProgress`` and fall
# back to a tiny dataclass with the same attributes if it is missing.
from faster_whisper import WhisperModel
try:  # pragma: no cover - simply for optional feature
    from faster_whisper import TranscriptionProgress  # type: ignore
except ImportError:  # pragma: no cover - executed when running with old lib
    from dataclasses import dataclass

    @dataclass
    class TranscriptionProgress:  # type: ignore
        """Fallback progress information structure."""

        elapsed: float
        total: float
        segments_done: int
        step: int = 1

__all__ = ["transcribe_audio"]


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def transcribe_audio(
    input_audio: Union[str, Path],
    *,
    model_name: str = "large-v3",
    device: str = "cuda",
    out_path: Optional[Union[str, Path]] = None,
    beam_size: int = 5,
    language: str = "ru",
    logger=None,
    progress_handler: Optional[Callable[[TranscriptionProgress], None]] = None,
) -> Path:
    """Transcribe *input_audio* and save result to *out_path*.

    Parameters
    ----------
    input_audio : str | Path
        Path to the source audio file (wav / mp3 / m4a / …).
    model_name : str, default "large-v3"
        HF model ID or local directory with Faster‑Whisper weights.
    device : {"cuda", "cpu"}, default "cuda"
        Device for inference. If ``cuda`` is selected but not available, an
        exception will be raised by Faster‑Whisper.
    out_path : str | Path | None, default ``None``
        Where to save text output. If *None*, ``<input_audio>.txt`` is used.
    beam_size : int, default 5
        Beam‑search size.
    language : str, default "ru"
        ISO‑639‑1 language code or "auto" for autodetect.
    progress_handler : Callable[[TranscriptionProgress], None] | None
        Optional callback to receive progress updates from Faster‑Whisper.

    Returns
    -------
    Path
        Path to the generated text file.
    """

    # ---------------------------------------------------------------------
    # Подготовка путей
    # ---------------------------------------------------------------------
    audio_path = Path(input_audio).expanduser().resolve()
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    output_path = (
        Path(out_path).expanduser().resolve() if out_path else audio_path.with_suffix(".txt")
    )


    # ---------------------------------------------------------------------
    # Загрузка модели
    # ---------------------------------------------------------------------
    print(f"Загружаем модель {model_name} на {device}…")
    model = WhisperModel(
        model_name,
        device=device,
        compute_type="int8_float16" if device == "cuda" else "int8",
    )

    # ---------------------------------------------------------------------
    # Транскрибация с отображением прогресса
    # ---------------------------------------------------------------------

    print(f"Начинаем транскрибацию {audio_path.name}…")

    last_percent = -1
    progress_bar = tqdm(total=100, bar_format="{l_bar}{bar}| {n_fmt}%")

    def _internal_progress_cb(p: TranscriptionProgress):
        nonlocal last_percent
        if progress_handler:
            progress_handler(p)
        # Обновляем прогресс в консоли
        if p.total:
            percent = int(p.elapsed / p.total * 100)
            if percent != last_percent:
                progress_bar.update(percent - last_percent)
                last_percent = percent

    transcribe_kwargs = dict(
        language=None if language == "auto" else language,
        beam_size=beam_size,
        vad_filter=True,
    )

    # Некоторые версии faster_whisper не поддерживают параметр
    # ``progress_callback``.  Проверяем его наличие через introspection и
    # передаём, только если параметр присутствует.
    import inspect

    if "progress_callback" in inspect.signature(model.transcribe).parameters:
        transcribe_kwargs["progress_callback"] = _internal_progress_cb

    segments, _info = model.transcribe(str(audio_path), **transcribe_kwargs)

    if last_percent < 100:
        progress_bar.update(100 - last_percent)
    progress_bar.close()

    # ---------------------------------------------------------------------
    # Save result
    # ---------------------------------------------------------------------

    with open(output_path, "w", encoding="utf-8") as fp:
        for seg in segments:
            # [hh:mm:ss.mmm --> hh:mm:ss.mmm] text
            hh = lambda t: f"{int(t // 3600):02d}:{int((t % 3600) // 60):02d}:{t % 60:06.3f}"
            line = f"[{hh(seg.start)} --> {hh(seg.end)}] {seg.text.strip()}\n"
            fp.write(line)

    print(f"Транскрибация завершена. Файл сохранён: {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# CLI wrapper
# ---------------------------------------------------------------------------


def _parse_cli_args() -> argparse.Namespace:  # pragma: no cover
    p = argparse.ArgumentParser(prog="transcriber", description="Audio transcription helper")
    p.add_argument("input_audio", help="Path to .wav / .mp3 / .m4a …")
    p.add_argument("--model", default="large-v3", help="HF model name or local dir")
    p.add_argument("--device", default="cuda", choices=["cuda", "cpu"], help="Device to run on")
    p.add_argument("--out", help="Where to save text (default: <input>.txt)")
    p.add_argument("--beam_size", type=int, default=5, help="Beam size")
    p.add_argument("--language", default="ru", help="ISO code or auto")
    return p.parse_args()



def main() -> None:  # pragma: no cover – CLI only
    args = _parse_cli_args()

    transcribe_audio(
        args.input_audio,
        model_name=args.model,
        device=args.device,
        out_path=args.out,
        beam_size=args.beam_size,
        language=args.language,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
