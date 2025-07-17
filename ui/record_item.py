"""Виджет одной записи в списке файлов."""

from __future__ import annotations

import os
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QMessageBox

from style import (LABEL_TEXT, SURFACE_CONTAINER_HIGH, SURFACE_CONTAINER_HIGHEST, ON_SURFACE, SURFACE_VARIANT, ON_SURFACE_VARIANT, PRIMARY, ON_PRIMARY)
from .utils import open_in_folder, open_file


class RecordItem(QFrame):
    """Элемент списка сохранённых записей со всеми действиями."""

    def __init__(self, path: str, settings, transcribe_cb=None, parent=None) -> None:
        super().__init__(parent)
        self.path = path
        self._settings = settings
        self._transcribe_cb = transcribe_cb
        self._txt_path = self._calc_transcript_path(path)
        self.setFixedHeight(56)

        # --- Material Design 3 record item styling ---
        self.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE_CONTAINER_HIGH};
                border-radius: 16px;
                border: none;
            }}
            QFrame:hover {{
                background: {SURFACE_CONTAINER_HIGHEST};
            }}
            QLabel {{
                color: {ON_SURFACE};
                font-size: 14px;
                font-weight: 400;
            }}
            QPushButton {{
                background: {SURFACE_VARIANT};
                color: {ON_SURFACE_VARIANT};
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
                min-width: 32px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background: {PRIMARY};
                color: {ON_PRIMARY};
            }}
            QPushButton:pressed {{
                background: {PRIMARY};
                color: {ON_PRIMARY};
            }}
        """)

        # --- Material Design 3 horizontal layout ---
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(20, 12, 20, 12)
        hbox.setSpacing(12)

        self.name_lbl = QLabel(os.path.basename(path))
        self.name_lbl.setStyleSheet(f"""
            color: {ON_SURFACE};
            font-weight: 500;
        """)
        hbox.addWidget(self.name_lbl, stretch=1)

        # Material Design 3 icon buttons
        show_btn = QPushButton("📂")
        show_btn.setFixedSize(40, 32)
        show_btn.setToolTip("Открыть папку")
        show_btn.clicked.connect(lambda: open_in_folder(path))
        hbox.addWidget(show_btn)

        rename_btn = QPushButton("✎")
        rename_btn.setFixedSize(40, 32)
        rename_btn.setToolTip("Переименовать")
        rename_btn.clicked.connect(self.rename_file)
        hbox.addWidget(rename_btn)

        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(40, 32)
        delete_btn.setToolTip("Удалить")
        delete_btn.clicked.connect(self.delete_file)
        hbox.addWidget(delete_btn)

        trans_btn = QPushButton("📝")
        trans_btn.setFixedSize(40, 32)
        trans_btn.setToolTip("Транскрибировать")
        trans_btn.clicked.connect(self.transcribe_file)
        hbox.addWidget(trans_btn)

        self.open_txt_btn = QPushButton("📄")
        self.open_txt_btn.setFixedSize(40, 32)
        self.open_txt_btn.setToolTip("Открыть транскрипт")
        self.open_txt_btn.clicked.connect(self.open_transcript)
        self.open_txt_btn.setVisible(os.path.exists(self._txt_path))
        hbox.addWidget(self.open_txt_btn)

    # ------------------------------------------------------------------
    # вспомогательные методы
    # ------------------------------------------------------------------
    def _calc_transcript_path(self, audio_path: str) -> str:
        folder = self._settings.transcript_folder()
        if not folder:
            folder = os.path.dirname(audio_path)
        base = os.path.splitext(os.path.basename(audio_path))[0] + ".txt"
        return os.path.join(folder, base)

    def transcript_path(self) -> str:
        return self._txt_path

    def set_transcript_path(self, path: str) -> None:
        self._txt_path = path
        self.open_txt_btn.setVisible(os.path.exists(path))

    def open_transcript(self) -> None:
        open_file(self._txt_path)

    def rename_file(self) -> None:
        from PyQt6.QtWidgets import QInputDialog

        folder = os.path.dirname(self.path)
        current_name = os.path.basename(self.path)
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=current_name)
        if ok and new_name:
            if not new_name.lower().endswith(os.path.splitext(current_name)[1]):
                new_name += os.path.splitext(current_name)[1]
            new_path = os.path.join(folder, new_name)
            try:
                os.rename(self.path, new_path)
            except OSError:
                return
            old_path = self.path
            self.path = new_path

            # перемещаем также текстовую транскрипцию, если она есть
            old_txt = self._calc_transcript_path(old_path)
            new_txt = self._calc_transcript_path(new_path)
            if os.path.exists(old_txt):
                try:
                    os.rename(old_txt, new_txt)
                except OSError:
                    pass
            self.set_transcript_path(new_txt)
            self.name_lbl.setText(new_name)
            records = self._settings.records()
            for i, p in enumerate(records):
                if p == old_path:
                    records[i] = new_path
                    break
            self._settings.set_records(records)

    def delete_file(self) -> None:
        """Удалить запись и текстовый файл, обновить список."""
        reply = QMessageBox.question(
            self,
            "Удалить запись",
            "Вы уверены, что хотите удалить файл?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(self.path)
            except OSError:
                pass
            txt = self._calc_transcript_path(self.path)
            if os.path.exists(txt):
                try:
                    os.remove(txt)
                except OSError:
                    pass
            records = [p for p in self._settings.records() if p != self.path]
            self._settings.set_records(records)
            self.setParent(None)
            self.deleteLater()

    def transcribe_file(self) -> None:
        """Передать файл на транскрибацию через внешний колбэк."""
        if self._transcribe_cb:
            self._transcribe_cb(self.path, self)
