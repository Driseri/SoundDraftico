from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QStackedLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
import subprocess, sys
from ffmpeg_core import FFmpegProgressWatcher, get_audio_lines
import os, datetime
import threading
from audio2text import transcribe_audio

def open_in_folder(path: str):
    """Открыть папку, содержащую указанный файл."""
    folder = os.path.abspath(os.path.dirname(path))
    if sys.platform.startswith("win"):
        os.startfile(folder)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", folder])
    else:
        subprocess.Popen(["xdg-open", folder])


class RecordItem(QFrame):
    """Элемент списка сохранённых записей."""

    def __init__(self, path: str, settings, transcribe_cb=None, parent=None):
        super().__init__(parent)
        self.path = path
        self._settings = settings
        self._transcribe_cb = transcribe_cb
        self.setFixedHeight(48)
        # Стилизация элемента
        self.setStyleSheet(
            f"""
            QFrame {{
                background: #222A36;
                border-radius: 12px;
            }}
            QLabel {{ color: {LABEL_TEXT}; font-size: 15px; }}
            QPushButton {{
                background: #323B4A;
                color: {LABEL_TEXT};
                border: none;
                border-radius: 8px;
                font-size: 16px;
                padding-bottom: 2px;
            }}
            QPushButton:hover {{ background: #48516B; }}
            """
        )
        # Основная горизонтальная раскладка
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(16, 8, 16, 8)
        hbox.setSpacing(12)

        self.name_lbl = QLabel(os.path.basename(path))
        hbox.addWidget(self.name_lbl, stretch=1)

        # Кнопка открытия расположения файла
        show_btn = QPushButton("📂")
        show_btn.setFixedWidth(36)
        show_btn.clicked.connect(lambda: open_in_folder(path))
        hbox.addWidget(show_btn)

        # Кнопка переименования
        rename_btn = QPushButton("✎")
        rename_btn.setFixedWidth(36)
        rename_btn.clicked.connect(self.rename_file)
        hbox.addWidget(rename_btn)

        # Кнопка удаления файла
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedWidth(36)
        delete_btn.clicked.connect(self.delete_file)
        hbox.addWidget(delete_btn)

        # Кнопка транскрибации
        trans_btn = QPushButton("📝")
        trans_btn.setFixedWidth(36)
        trans_btn.clicked.connect(self.transcribe_file)
        hbox.addWidget(trans_btn)

    def rename_file(self):
        from PyQt6.QtWidgets import QInputDialog
        # Диалоговое окно переименования файла
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
            self.name_lbl.setText(new_name)
            # обновляем список записей в настройках
            records = self._settings.records()
            for i, p in enumerate(records):
                if p == old_path:
                    records[i] = new_path
                    break
            self._settings.set_records(records)

    def delete_file(self):
        """Удалить запись и обновить список."""
        # Подтверждаем удаление файла
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
            records = [p for p in self._settings.records() if p != self.path]
            self._settings.set_records(records)
            self.setParent(None)
            self.deleteLater()

    def transcribe_file(self):
        """Отправить файл на транскрибацию через переданный колбэк."""
        if self._transcribe_cb:
            self._transcribe_cb(self.path)

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
        self.trans_timer = QTimer()
        self.trans_timer.timeout.connect(self._poll_trans_progress)
        self.trans_thread = None
        self.trans_percent = 0
        
        self.setFixedWidth(540)
        self.setObjectName("left_frame")
        self.setStyleSheet(f"""
            QFrame#left_frame {{
                background: {BG_LEFT};
                border-radius: 20px;
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
        settings_btn.setFixedSize(38, 38)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SETTINGS_BG};
                color: {SETTINGS_TEXT};
                border: none;
                border-radius: 18px;
                font-size: 19px;
            }}
            QPushButton:hover {{
                background: {TAB_ACTIVE};
            }}
        """)
        settings_btn.clicked.connect(self.show_settings)
        left_main_vbox.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Вкладки
        tab_row = QHBoxLayout()
        tab_live = QPushButton("● Live")
        tab_live.setEnabled(False)
        tab_live.setFixedHeight(32)
        tab_live.setFixedWidth(90)
        tab_live.setStyleSheet(f"""
            QPushButton {{
                background: {TAB_ACTIVE};
                color: {TAB_ACTIVE_TEXT};
                border-radius: 15px;
                font-weight: bold;
            }}
        """)
        tab_off = QPushButton("Offline")
        tab_off.setFixedHeight(32)
        tab_off.setFixedWidth(90)
        tab_off.setStyleSheet(f"""
            QPushButton {{
                background: {TAB_INACTIVE};
                color: {TAB_INACTIVE_TEXT};
                border-radius: 15px;
            }}
        """)
        tab_row.addWidget(tab_live)
        tab_row.addWidget(tab_off)
        left_main_vbox.addLayout(tab_row)

        # Кнопки управления
        ctrl_row = QHBoxLayout()
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(44, 44)
        self.btn_play.setStyleSheet(f"""
            QPushButton {{
                background: {BTN_PLAY};
                color: {BTN_TEXT};
                font-size: 19px;
                border-radius: 22px;
            }}
            QPushButton:hover {{ background: #40954A; }}
        """)
        self.btn_stop = QPushButton("■")
        self.btn_stop.setFixedSize(44, 44)
        self.btn_stop.setStyleSheet(f"""
            QPushButton {{
                background: {BTN_STOP};
                color: {BTN_TEXT};
                font-size: 19px;
                border-radius: 22px;
            }}
            QPushButton:hover {{ background: #FF5507; }}
        """)
        
        ctrl_row.addWidget(self.btn_play)
        ctrl_row.addWidget(self.btn_stop)
        left_main_vbox.addLayout(ctrl_row)

        # ---- info frame for current recording ----
        self.record_frame = QFrame()
        self.record_frame.setStyleSheet(
            """
            QFrame {
                background: #222A36;
                border-radius: 12px;
            }
            QLabel {
                font-size: 15px;
            }
            """
        )

        info_hbox = QHBoxLayout(self.record_frame)
        info_hbox.setContentsMargins(16, 8, 16, 8)
        info_hbox.setSpacing(12)

        self.file_lbl = QLabel()
        self.file_lbl.setStyleSheet(f"color: {COLOR_ACCENT};")

        self.time_lbl = QLabel("00:00:00")
        self.time_lbl.setStyleSheet(f"color: {LABEL_TEXT};")

        self.size_lbl = QLabel("0 KB")
        self.size_lbl.setStyleSheet(f"color: {SETTINGS_TEXT};")

        info_hbox.addWidget(self.file_lbl)
        info_hbox.addWidget(self.time_lbl)
        info_hbox.addWidget(self.size_lbl)

        self.record_frame.setVisible(False)
        left_main_vbox.addWidget(self.record_frame)

        self.btn_stop.setEnabled(False)

        self.btn_play.clicked.connect(self.start_record)
        self.btn_stop.clicked.connect(self.stop_record)


        # --- Список записей ---
        status_lbl = QLabel("Записи")
        status_lbl.setStyleSheet(
            f"color: {LABEL_TEXT}; font-size:16px; font-weight: bold; margin-left:18px;"
        )
        left_main_vbox.addWidget(status_lbl)

        self.records_scroll = QScrollArea()
        self.records_scroll.setWidgetResizable(True)
        self.records_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.records_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.records_scroll.setStyleSheet("background: transparent; border: none;")
        self.records_widget = QWidget()
        self.records_layout = QVBoxLayout(self.records_widget)
        self.records_layout.setContentsMargins(18, 4, 18, 4)
        self.records_layout.setSpacing(8)
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
            # start transcription in background
            self._start_transcription(result["output_file"])
        else:
            self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), "ERROR Record failed", "#FF7043")])
        self.ffmpeg = None
        self.record_frame.setVisible(False)

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
        if bytes_size >= 1024 ** 3:
            return f"{bytes_size / (1024 ** 3):.1f} GB"
        elif bytes_size >= 1024 ** 2:
            return f"{bytes_size / (1024 ** 2):.1f} MB"
        elif bytes_size >= 1024:
            return f"{bytes_size / 1024:.1f} KB"
        else:
            return f"{bytes_size} B"

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

    def _start_transcription(self, path: str):
        """Start transcription of *path* in a background thread."""
        if self.trans_thread:
            return

        self.trans_percent = 0
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.insert_log([(stamp, f"INFO Transcribing → {os.path.basename(path)}", "#4DC3F6")])

        def progress_cb(p):
            if p.total:
                self.trans_percent = int(p.elapsed / p.total * 100)

        def worker():
            try:
                out = transcribe_audio(path, progress_handler=progress_cb, logger=None)
                self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), f"INFO Transcript → {out}", "#4DC3F6")])
            except Exception as exc:  # pragma: no cover - GUI feedback only
                self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), f"ERROR {exc}", "#FF7043")])
            finally:
                self.trans_thread = None

        self.trans_thread = threading.Thread(target=worker, daemon=True)
        self.trans_thread.start()
        self.trans_timer.start(1000)

    def _poll_trans_progress(self):
        if self.trans_thread:
            self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), f"Progress {self.trans_percent}%", "#AAB8CC")])
            if not self.trans_thread.is_alive():
                self.trans_timer.stop()
        else:
            self.trans_timer.stop()

