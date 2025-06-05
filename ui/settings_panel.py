from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QFrame,
)
from ffmpeg_core import get_audio_lines
from PyQt6.QtCore import Qt
from style import *
from ui.settings_manager import SettingsManager
import os

class SettingsPanel(QWidget):
    """Виджет с настройками приложения."""
    def __init__(self, back_callback, settings: SettingsManager):
        super().__init__()
        self._settings = settings
        self.setStyleSheet("background: transparent;")
        # Основная вертикальная раскладка
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(24, 18, 24, 24)
        vbox.setSpacing(12)
        # Кнопка возврата к основному экрану
        back_btn = QPushButton("← Назад")
        back_btn.setFixedWidth(92)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: {TAB_ACTIVE};
                color: {TAB_ACTIVE_TEXT};
                border-radius: 15px;
                font-weight: bold;
            }}
        """)
        back_btn.clicked.connect(back_callback)
        vbox.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Заголовок раздела
        settings_lbl = QLabel("Настройки")
        settings_lbl.setStyleSheet(f"color: {LABEL_TEXT}; font-size: 22px; font-weight: bold; margin-left:22px;")
        vbox.addWidget(settings_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        # --- Список аудио-устройств ---
        devices = get_audio_lines()
        self.device_combo = QComboBox()
        self.device_combo.setStyleSheet("""
            background: #232A36;
            color: #AAB8CC;
            border-radius: 6px;
        """)
        self.device_combo.setFixedWidth(260)
        if devices:
            self.device_combo.addItems(devices)
        else:
            self.device_combo.addItem("<не найдено>")

        # Используем ранее выбранное устройство, если оно сохранено
        stored_device = self._settings.device("")
        if stored_device:
            idx = self.device_combo.findText(stored_device)
            if idx >= 0:
                self.device_combo.setCurrentIndex(idx)

        self.device_frame = InputFrame("Устройство записи:", self.device_combo)
        vbox.addWidget(self.device_frame)

        # --- Прямоугольная панель для выбора папки ---
        initial_folder = self._settings.folder(os.path.expanduser("~/Documents"))
        self.folder_frame = FolderSelectFrame(
            "Папка для сохранения:",
            initial_value=initial_folder,
        )
        self.folder_frame.set_on_click(self.choose_save_folder)
        vbox.addWidget(self.folder_frame)

        # --- Папка для текстовых транскрипций ---
        initial_txt_folder = self._settings.transcript_folder(initial_folder)
        self.trans_folder_frame = FolderSelectFrame(
            "Папка транскрипций:",
            initial_value=initial_txt_folder,
        )
        self.trans_folder_frame.set_on_click(self.choose_transcript_folder)
        vbox.addWidget(self.trans_folder_frame)


        f2_lbl = QLabel("Язык по умолчанию:")
        f2_lbl.setStyleSheet(f"color: {LABEL_TEXT}; font-size: 15px; margin-left:36px;")
        vbox.addWidget(f2_lbl)
        f2_entry = QLineEdit()
        f2_entry.setFixedWidth(260)
        f2_entry.setStyleSheet("margin-left:36px;")
        vbox.addWidget(f2_entry)
        vbox.addStretch(1)

    def selected_device(self) -> str:
        """Вернуть выбранное пользователем устройство."""
        return self.device_combo.currentText()
    
    def choose_save_folder(self):
        # Выбор каталога для сохранения аудиофайлов
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку для аудиозаписей", self.folder_frame.value()
        )
        if folder:
            self.folder_frame.set_value(folder)

    def choose_transcript_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Папка для транскрипций", self.trans_folder_frame.value()
        )
        if folder:
            self.trans_folder_frame.set_value(folder)

    def save_settings(self):
        """Сохранить текущие настройки через SettingsManager."""
        self._settings.set_device(self.selected_device())
        self._settings.set_folder(self.save_folder())
        self._settings.set_transcript_folder(self.transcript_folder())


    def save_folder(self) -> str:
        return self.folder_frame.value()

    def transcript_folder(self) -> str:
        return self.trans_folder_frame.value()
    

class FolderSelectFrame(QFrame):
    """Поле выбора папки с кнопкой обзора."""
    def __init__(self, label_text, initial_value="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: #222A36;
                border-radius: 12px;
            }}
        """)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(16, 8, 16, 8)
        hbox.setSpacing(12)
        
        self.label = QLabel(label_text)
        self.label.setStyleSheet("color: #AAB8CC; font-size: 15px;")
        self.lineedit = QLineEdit()
        self.lineedit.setText(initial_value)
        self.lineedit.setStyleSheet("""
            background: #232A36;
            color: #AAB8CC;
            border-radius: 6px;
            padding: 2px 8px;
        """)
        self.button = QPushButton("…")
        self.button.setFixedWidth(36)
        self.button.setStyleSheet("""
            QPushButton {
                background: #323B4A;
                color: #AAB8CC;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                padding-bottom: 2px;
            }
            QPushButton:hover { background: #48516B; }
        """)
        hbox.addWidget(self.label)
        hbox.addWidget(self.lineedit, stretch=1)
        hbox.addWidget(self.button)

    def set_on_click(self, callback):
        self.button.clicked.connect(callback)

    def value(self):
        return self.lineedit.text()

    def set_value(self, text):
        self.lineedit.setText(text)

class InputFrame(QFrame):
    """Контейнер с подписью и вложенным виджетом."""
    def __init__(self, label_text, widget, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: #222A36;
                border-radius: 12px;
            }
        """)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(16, 8, 16, 8)
        hbox.setSpacing(12)
        label = QLabel(label_text)
        label.setStyleSheet("color: #AAB8CC; font-size: 15px;")
        hbox.addWidget(label)
        hbox.addWidget(widget, stretch=1)