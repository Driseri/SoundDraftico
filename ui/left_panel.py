"""Левая панель приложения со списком записей и управлением записью."""

from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QStackedLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer
import datetime
import os
import threading
from ffmpeg_core import FFmpegProgressWatcher, get_audio_lines
from audio2text import transcribe_audio

from .record_item import RecordItem
from .utils import format_size

from style import *
from ui.settings_panel import SettingsPanel
from ui.settings_manager import SettingsManager

class LeftPanel(QFrame):
    def __init__(self, console_panel):
        super().__init__()
        self.console = console_panel          # ссылка на ConsolePanel
        self.settings = SettingsManager()
        self.ffmpeg = None                    # активный FFmpegProgressWatcher
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._poll_progress)
        self.trans_thread = None
        
        self.setFixedWidth(580)
        self.setObjectName("left_frame")
        self.setStyleSheet(f"""
            QFrame#left_frame {{
                background: {SURFACE_CONTAINER};
                border-radius: 16px;
                border: none;
            }}
        """)
        frame_layout = QVBoxLayout(self)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # --- Стек для основного контента и настроек ---
        self.left_stack = QStackedLayout()
        frame_layout.addLayout(self.left_stack)

        # --- Основной экран
        self.left_main_widget = QWidget()
        self.left_main_widget.setStyleSheet("background: transparent;")
        left_main_vbox = QVBoxLayout(self.left_main_widget)
        left_main_vbox.setContentsMargins(24, 18, 24, 24)
        left_main_vbox.setSpacing(12)

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(48, 48)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE_CONTAINER_HIGH};
                color: {ON_SURFACE_VARIANT};
                border: none;
                border-radius: 24px;
                font-size: 20px;
                font-weight: 400;
            }}
            QPushButton:hover {{
                background: {SURFACE_CONTAINER_HIGHEST};
                color: {ON_SURFACE};
            }}
            QPushButton:pressed {{
                background: {PRIMARY};
                color: {ON_PRIMARY};
            }}
        """)
        settings_btn.clicked.connect(self.show_settings)
        left_main_vbox.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Material Design 3 Segmented Button (Tabs)
        tab_row = QHBoxLayout()
        tab_row.setSpacing(4)
        
        tab_live = QPushButton("● Live")
        tab_live.setEnabled(False)
        tab_live.setFixedHeight(40)
        tab_live.setFixedWidth(100)
        tab_live.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY_CONTAINER};
                color: {ON_PRIMARY_CONTAINER};
                border: none;
                border-radius: 20px;
                font-weight: 500;
                font-size: 14px;
            }}
        """)
        
        tab_off = QPushButton("Offline")
        tab_off.setFixedHeight(40)
        tab_off.setFixedWidth(100)
        tab_off.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {ON_SURFACE_VARIANT};
                border: 1px solid {SURFACE_VARIANT};
                border-radius: 20px;
                font-weight: 500;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(103, 80, 164, 0.08);
                color: {ON_SURFACE};
            }}
        """)
        
        tab_row.addWidget(tab_live)
        tab_row.addWidget(tab_off)
        tab_row.addStretch()
        left_main_vbox.addLayout(tab_row)

        # Material Design 3 FAB-style control buttons
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(16)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.clicked.connect(self.start_recording)
        self.btn_play.setFixedSize(56, 56)
        self.btn_play.setStyleSheet(f"""
            QPushButton {{
                background: {SUCCESS_CONTAINER};
                color: {SUCCESS};
                font-size: 20px;
                font-weight: 500;
                border: none;
                border-radius: 28px;
            }}
            QPushButton:hover {{
                background: {SUCCESS};
                color: {ON_SUCCESS};
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
            }}
            QPushButton:pressed {{
                background: {SUCCESS};
                color: {ON_SUCCESS};
                box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);
            }}
        """)
        
        self.btn_stop = QPushButton("■")
        self.btn_stop.clicked.connect(self.stop_recording)
        self.btn_stop.setFixedSize(56, 56)
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background: {ERROR_CONTAINER};
                color: {ERROR};
                font-size: 18px;
                font-weight: 500;
                border: none;
                border-radius: 28px;
            }}
            QPushButton:hover {{
                background: {ERROR};
                color: {ON_ERROR};
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
            }}
            QPushButton:pressed {{
                background: {ERROR};
                color: {ON_ERROR};
                box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);
            }}
        """)
        
        ctrl_row.addWidget(self.btn_play)
        ctrl_row.addWidget(self.btn_stop)
        ctrl_row.addStretch()
        left_main_vbox.addLayout(ctrl_row)

        # ---- Material Design 3 info card for current recording ----
        self.record_frame = QFrame()
        self.record_frame.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE_CONTAINER_HIGH};
                border-radius: 16px;
                border: none;
            }}
            QLabel {{
                font-size: 14px;
                font-weight: 400;
            }}
        """)

        info_hbox = QHBoxLayout(self.record_frame)
        info_hbox.setContentsMargins(20, 12, 20, 12)
        info_hbox.setSpacing(16)

        self.file_lbl = QLabel()
        self.file_lbl.setStyleSheet(f"""
            color: {PRIMARY};
            font-weight: 500;
        """)

        self.time_lbl = QLabel("00:00:00")
        self.time_lbl.setStyleSheet(f"""
            color: {ON_SURFACE};
            font-weight: 500;
            font-family: 'Consolas', 'Monaco', monospace;
        """)

        self.size_lbl = QLabel("0 KB")
        self.size_lbl.setStyleSheet(f"""
            color: {ON_SURFACE_VARIANT};
            font-weight: 400;
        """)

        info_hbox.addWidget(self.file_lbl, 1)
        info_hbox.addWidget(self.time_lbl)
        info_hbox.addWidget(self.size_lbl)

        self.record_frame.setVisible(False)
        left_main_vbox.addWidget(self.record_frame)

        self.btn_stop.setEnabled(False)

        self.btn_play.clicked.connect(self.start_record)
        self.btn_stop.clicked.connect(self.stop_record)


        # --- Material Design 3 Records List ---
        status_lbl = QLabel("Записи")
        status_lbl.setStyleSheet(f"""
            color: {ON_SURFACE};
            font-size: 18px;
            font-weight: 500;
            margin-left: 20px;
            margin-top: 8px;
            margin-bottom: 4px;
        """)
        left_main_vbox.addWidget(status_lbl)

        self.records_scroll = QScrollArea()
        self.records_scroll.setWidgetResizable(True)
        self.records_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.records_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.records_scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
                border-radius: 8px;
            }}
        """)
        self.records_scroll.verticalScrollBar().setStyleSheet(SCROLLBAR_STYLE)
        
        self.records_widget = QWidget()
        self.records_widget.setStyleSheet("background: transparent;")
        self.records_layout = QVBoxLayout(self.records_widget)
        self.records_layout.setContentsMargins(20, 8, 20, 8)
        self.records_layout.setSpacing(12)
        self.records_scroll.setWidget(self.records_widget)
        left_main_vbox.addWidget(self.records_scroll, 1)

        self._load_records()

        # --- Экран настроек
        self.left_settings_widget = SettingsPanel(self.show_main, self.settings)
        self.left_stack.addWidget(self.left_main_widget)
        self.left_stack.addWidget(self.left_settings_widget)
        self.left_stack.setCurrentWidget(self.left_main_widget)

    def show_settings(self):
        self.left_stack.setCurrentWidget(self.left_settings_widget)
    def show_main(self):
        # save settings when leaving the settings view
        self.left_settings_widget.save_settings()
        self.left_stack.setCurrentWidget(self.left_main_widget)

        # --- доступ к настройкам ---
    def _current_device(self) -> str:
        return self.left_settings_widget.device_combo.currentText()

    def _save_folder(self) -> str:
        return self.left_settings_widget.folder_frame.value()

    def _transcript_folder(self) -> str:
        return self.left_settings_widget.trans_folder_frame.value()

    def start_record(self):
        if self.ffmpeg:     # уже пишется — ничего не делаем!
            return
        
        self.btn_play.setEnabled(False)   # Делаем кнопку "Record" неактивной
        self.btn_stop.setEnabled(True)
        # путь и имя файла
        folder = self._save_folder()
        os.makedirs(folder, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = os.path.join(folder, f"{stamp}.mp3")
        self.current_file = out_file

        # watcher
        self.ffmpeg = FFmpegProgressWatcher(
            device_name=self._current_device(),
            output_file=out_file,
            bitrate="128k"
        )
        self.ffmpeg.start()
        self.console.insert_log([(stamp, f"INFO Recording → {out_file}", "#4DC3F6")])
        self.progress_timer.start(1000)   # раз в сек
        self.file_lbl.setText(os.path.basename(out_file))
        self.time_lbl.setText("00:00:00")
        self.size_lbl.setText("0 KB")
        self.record_frame.setVisible(True)

    def stop_record(self):
        if not self.ffmpeg:
            return
        
        self.btn_play.setEnabled(True)    # Можно снова начинать запись
        self.btn_stop.setEnabled(False)     # Пока нечего останавливать

        result = self.ffmpeg.stop()
        self.progress_timer.stop()
        if result["success"]:
            msg = f"Saved: {result['output_file']} · {result['duration']}"
            self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), msg, "#4DC3F6")])
            self.time_lbl.setText(result["duration"])
            self.size_lbl.setText(self._format_size(result.get("size_bytes", 0)))
            # persist record info
            records = self.settings.records()
            if result["output_file"] not in records:
                records.append(result["output_file"])
                self.settings.set_records(records)
            self._add_record_item(result["output_file"])
        else:
            self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), "ERROR Record failed", "#FF7043")])
        self.ffmpeg = None
        self.record_frame.setVisible(False)

    def start_recording(self):
        self.console.set_recording_state(True)
        # Add recording logic here

    def stop_recording(self):
        self.console.set_recording_state(False)
        # Add stop recording logic here

    def _poll_progress(self):
        if self.ffmpeg:
            out_time, size, speed = self.ffmpeg.get_last_progress()
            txt = f"{out_time}  {int(size)//1024} KB  {speed}"
            self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), txt, "#AAB8CC")])
            self.time_lbl.setText(out_time)
            try:
                bytes_size = int(size)
            except ValueError:
                bytes_size = 0
            self.size_lbl.setText(self._format_size(bytes_size))

    def _format_size(self, bytes_size: int) -> str:
        """Отформатировать размер файла для отображения."""
        return format_size(bytes_size)

    def _load_records(self):
        """Загрузить сохранённые записи из настроек."""
        for path in self.settings.records():
            if os.path.exists(path):
                self._add_record_item(path)

    def _add_record_item(self, path: str):
        """Добавить запись в список на панели."""
        item = RecordItem(path, self.settings, self._start_transcription)
        self.records_layout.addWidget(item)

    # ------------------------------------------------------------------
    #  Transcription handling
    # ------------------------------------------------------------------

    def _start_transcription(self, path: str, item: RecordItem):
        """Start transcription of *path* in a background thread."""
        if self.trans_thread:
            return

        stamp = datetime.datetime.now().strftime("%H:%M:%S")

        out_folder = self._transcript_folder()
        os.makedirs(out_folder, exist_ok=True)
        out_path = os.path.join(out_folder, os.path.splitext(os.path.basename(path))[0] + ".txt")

        def worker():
            try:
                transcribe_audio(path, out_path=out_path)
                item.set_transcript_path(out_path)
            except Exception as exc:  # pragma: no cover - GUI feedback only
                self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), f"ERROR {exc}", "#FF7043")])
            finally:
                self.trans_thread = None

        self.trans_thread = threading.Thread(target=worker, daemon=True)
        self.trans_thread.start()

