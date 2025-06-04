from PyQt6.QtWidgets import QFrame, QVBoxLayout, QStackedLayout, QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame
from PyQt6.QtCore import Qt, QTimer
from ffmpeg_core import FFmpegProgressWatcher, get_audio_lines
from style import *
from ui.settings_panel import SettingsPanel
from ui.settings_manager import SettingsManager
import os, datetime

class LeftPanel(QFrame):
    def __init__(self, console_panel):
        super().__init__()
        self.console = console_panel          # ссылка на ConsolePanel
        self.settings = SettingsManager()
        self.ffmpeg = None                    # активный FFmpegProgressWatcher
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._poll_progress)
        
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

        self.btn_stop.setEnabled(False)

        self.btn_play.clicked.connect(self.start_record)
        self.btn_stop.clicked.connect(self.stop_record)


        # Статус и имитация текста
        status_lbl = QLabel("Status")
        status_lbl.setStyleSheet(f"color: {LABEL_TEXT}; font-size:16px; font-weight: bold; margin-left:18px;")
        left_main_vbox.addWidget(status_lbl)

        for _ in range(2):
            txt = QLabel("ТЕКСТ")
            txt.setStyleSheet(f"color: {TRANSCRIPT_TEXT}; font-size: 22px; font-weight: bold; margin-left:28px;")
            left_main_vbox.addWidget(txt)
            line = QFrame()
            line.setFixedHeight(7)
            line.setFixedWidth(170)
            line.setStyleSheet(f"background: {LINE}; border-radius: 3px; margin-left:32px;")
            left_main_vbox.addWidget(line)
        txt = QLabel("ТЕКСТ")
        txt.setStyleSheet(f"color: {TRANSCRIPT_TEXT}; font-size: 22px; font-weight: bold; margin-left:28px;")
        left_main_vbox.addWidget(txt)
        line = QFrame()
        line.setFixedHeight(7)
        line.setFixedWidth(140)
        line.setStyleSheet(f"background: {LINE}; border-radius: 3px; margin-left:32px;")
        left_main_vbox.addWidget(line)
        left_main_vbox.addStretch(1)

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

        # watcher
        self.ffmpeg = FFmpegProgressWatcher(
            device_name=self._current_device(),
            output_file=out_file,
            bitrate="128k"
        )
        self.ffmpeg.start()
        self.console.insert_log([(stamp, f"INFO Recording → {out_file}", "#4DC3F6")])
        self.progress_timer.start(1000)   # раз в сек

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
        else:
            self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), "ERROR Record failed", "#FF7043")])
        self.ffmpeg = None

    def _poll_progress(self):
        if self.ffmpeg:
            out_time, size, speed = self.ffmpeg.get_last_progress()
            txt = f"{out_time}  {int(size)//1024} KB  {speed}"
            self.console.insert_log([(datetime.datetime.now().strftime("%H:%M:%S"), txt, "#AAB8CC")])

