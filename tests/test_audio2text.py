import builtins
import logging
from pathlib import Path
import types
import tempfile
import importlib
import sys

class DummyProgress:
    def __init__(self, elapsed, total, segments_done, step=1):
        self.elapsed = elapsed
        self.total = total
        self.segments_done = segments_done
        self.step = step

class DummyWhisperModel:
    init_count = 0

    def __init__(self, *args, **kwargs):
        type(self).init_count += 1

    def transcribe(self, path, language=None, beam_size=5, vad_filter=True, progress_callback=None):
        total = 5
        for i in range(1, total + 1):
            if progress_callback:
                progress_callback(DummyProgress(i, total, i))
        segment = types.SimpleNamespace(start=0.0, end=1.0, text="hello")
        return [segment], {}

class DummyWhisperModelNoCb:
    """Модель без параметра progress_callback в методе transcribe."""

    def __init__(self, *args, **kwargs):
        pass

    # отсутствие параметра progress_callback имитирует старую версию библиотеки
    def transcribe(self, path, language=None, beam_size=5, vad_filter=True):
        segment = types.SimpleNamespace(start=0.0, end=1.0, text="hello")
        return [segment], {}


def test_model_caching(monkeypatch, tmp_path):
    """ensure that load_model caches WhisperModel instances"""

    dummy_module = types.SimpleNamespace(WhisperModel=DummyWhisperModel, TranscriptionProgress=DummyProgress)
    monkeypatch.setitem(sys.modules, "faster_whisper", dummy_module)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import importlib
    audio2text = importlib.import_module("audio2text")
    audio2text = importlib.reload(audio2text)
    monkeypatch.setattr(audio2text, "WhisperModel", DummyWhisperModel)

    DummyWhisperModel.init_count = 0
    m1 = audio2text.load_model()
    m2 = audio2text.load_model()
    assert m1 is m2
    assert DummyWhisperModel.init_count == 1

    temp_file = tmp_path / "dummy3.wav"
    temp_file.write_bytes(b"dummy")

    out = audio2text.transcribe_audio(temp_file, model=m1)
    assert Path(out).exists()
    assert DummyWhisperModel.init_count == 1

def test_transcribe_progress(monkeypatch, tmp_path):
    # Prepare stub for faster_whisper before importing module
    dummy_module = types.SimpleNamespace(WhisperModel=DummyWhisperModel, TranscriptionProgress=DummyProgress)
    monkeypatch.setitem(sys.modules, "faster_whisper", dummy_module)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import importlib
    audio2text = importlib.import_module("audio2text")
    audio2text = importlib.reload(audio2text)
    monkeypatch.setattr(audio2text, "WhisperModel", DummyWhisperModel)

    progress = []
    def handler(p):
        if p.total:
            progress.append(int(p.elapsed / p.total * 100))
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)
    temp_file = tmp_path / "dummy.wav"
    temp_file.write_bytes(b"dummy")

    out = audio2text.transcribe_audio(temp_file, logger=logger, progress_handler=handler)

    assert Path(out).exists()
    assert progress[-1] == 100


def test_transcribe_wo_progress_arg(monkeypatch, tmp_path):
    """Проверяем работу с моделью, где нет параметра progress_callback."""

    dummy_module = types.SimpleNamespace(WhisperModel=DummyWhisperModelNoCb, TranscriptionProgress=DummyProgress)
    monkeypatch.setitem(sys.modules, "faster_whisper", dummy_module)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import importlib
    audio2text = importlib.import_module("audio2text")
    audio2text = importlib.reload(audio2text)
    monkeypatch.setattr(audio2text, "WhisperModel", DummyWhisperModelNoCb)

    temp_file = tmp_path / "dummy2.wav"
    temp_file.write_bytes(b"dummy")

    out = audio2text.transcribe_audio(temp_file)

    assert Path(out).exists()

