import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from log_buffer import LogBuffer


def test_log_buffer_limit():
    buf = LogBuffer(max_entries=3)
    for i in range(5):
        buf.append(f"line {i}")
    assert len(buf.entries) == 3
    assert buf.entries[0] == "line 2"
