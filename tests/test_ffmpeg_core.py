import io
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ffmpeg_core


class DummyProcess:
    def __init__(self):
        self.stdout = io.StringIO("out_time=00:00:00.01\ntotal_size=100\nspeed=1x\n")
        self.stderr = io.StringIO()
        self.stdin = io.StringIO()
        self._returncode = None

    def poll(self):
        return self._returncode

    def wait(self, timeout=None):
        self._returncode = 0
        return 0

    def kill(self):
        self._returncode = -9


def test_stop_finishes(monkeypatch, tmp_path):
    def dummy_popen(*args, **kwargs):
        return DummyProcess()

    monkeypatch.setattr(ffmpeg_core.subprocess, "Popen", dummy_popen)
    out_file = tmp_path / "out.mp3"
    out_file.write_bytes(b"data")
    watcher = ffmpeg_core.FFmpegProgressWatcher("dummy", output_file=str(out_file))
    watcher.start()
    time.sleep(0.05)
    result = watcher.stop()
    assert result["success"]
    assert result["output_file"] == str(out_file)
