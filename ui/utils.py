"""Различные вспомогательные функции для UI."""

from __future__ import annotations

import os
import subprocess
import sys


def open_in_folder(path: str) -> None:
    """Открыть папку, содержащую указанный файл."""
    folder = os.path.abspath(os.path.dirname(path))
    if sys.platform.startswith("win"):
        os.startfile(folder)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", folder])
    else:
        subprocess.Popen(["xdg-open", folder])


def open_file(path: str) -> None:
    """Открыть *path* с помощью приложения по умолчанию."""
    if not os.path.exists(path):
        return
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def format_size(bytes_size: int) -> str:
    """Преобразовать размер в байтах в человекочитаемый вид."""
    if bytes_size >= 1024 ** 3:
        return f"{bytes_size / (1024 ** 3):.1f} GB"
    if bytes_size >= 1024 ** 2:
        return f"{bytes_size / (1024 ** 2):.1f} MB"
    if bytes_size >= 1024:
        return f"{bytes_size / 1024:.1f} KB"
    return f"{bytes_size} B"
