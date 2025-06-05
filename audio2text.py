"""
 transcriber.py – переиспользуемый модуль для транскрибации аудио через Faster‑Whisper
 с подробным логированием и возможностью отслеживать прогресс.

 Использование из кода::

     from transcriber import transcribe_audio
     text_file = transcribe_audio("/path/audio.m4a", logger=my_logger)

 Использование из CLI::

     python -m transcriber path/to/audio.wav --model large-v3 --device cuda

 Для логирования по умолчанию используется python logging; если logger не передан,
 создаётся собственный логгер transcriber с уровнем INFO.
 """

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Callable, Optional, Union

from faster_whisper import WhisperModel, TranscriptionProgress

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
    logger: Optional[logging.Logger] = None,
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
    logger : logging.Logger | None
        Existing logger to use. If *None*, a local one is created.
    progress_handler : Callable[[TranscriptionProgress], None] | None
        Optional callback to receive progress updates from Faster‑Whisper.

    Returns
    -------
    Path
        Path to the generated text file.
    """

    # ---------------------------------------------------------------------
    # Prepare paths & logger
    # ---------------------------------------------------------------------
    audio_path = Path(input_audio).expanduser().resolve()
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    output_path = (
        Path(out_path).expanduser().resolve() if out_path else audio_path.with_suffix(".txt")
    )

    log = logger or _get_default_logger()

    # ---------------------------------------------------------------------
    # Load model
    # ---------------------------------------------------------------------
    log.info("Loading model %s on %s …", model_name, device)
    model = WhisperModel(
        model_name,
        device=device,
        compute_type="int8_float16" if device == "cuda" else "int8",
    )

    # ---------------------------------------------------------------------
    # Transcription with progress reporting
    # ---------------------------------------------------------------------

    log.info("Transcribing %s …", audio_path.name)

    last_percent = -1

    def _internal_progress_cb(p: TranscriptionProgress):
        nonlocal last_percent
        if progress_handler:
            progress_handler(p)

        # Log progress each new percent if no external handler logs it
        if p.total:
            percent = int(p.elapsed / p.total * 100)
            if percent != last_percent:
                log.info("Progress: %d%% (%d segments)", percent, p.segments_done)
                last_percent = percent

    segments, _info = model.transcribe(
        str(audio_path),
        language=None if language == "auto" else language,
        beam_size=beam_size,
        vad_filter=True,
        progress_callback=_internal_progress_cb,
    )

    # ---------------------------------------------------------------------
    # Save result
    # ---------------------------------------------------------------------

    with open(output_path, "w", encoding="utf-8") as fp:
        for seg in segments:
            # [hh:mm:ss.mmm --> hh:mm:ss.mmm] text
            hh = lambda t: f"{int(t // 3600):02d}:{int((t % 3600) // 60):02d}:{t % 60:06.3f}"
            line = f"[{hh(seg.start)} --> {hh(seg.end)}] {seg.text.strip()}\n"
            fp.write(line)

    log.info("Done! Transcript saved to %s", output_path)
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
    p.add_argument(
        "--quiet", action="store_true", help="Silence INFO messages (show WARN and above)"
    )
    return p.parse_args()


def _get_default_logger(level: int = logging.INFO) -> logging.Logger:
    log = logging.getLogger("transcriber")
    if not log.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)8s | %(message)s"))
        log.addHandler(handler)
    log.setLevel(level)
    return log


def main() -> None:  # pragma: no cover – CLI only
    args = _parse_cli_args()
    level = logging.WARNING if args.quiet else logging.INFO
    logger = _get_default_logger(level)

    transcribe_audio(
        args.input_audio,
        model_name=args.model,
        device=args.device,
        out_path=args.out,
        beam_size=args.beam_size,
        language=args.language,
        logger=logger,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
