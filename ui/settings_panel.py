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
        # Material Design 3 back button
        back_btn = QPushButton("← Назад")
        back_btn.setFixedHeight(40)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE_CONTAINER_HIGH};
                color: {ON_SURFACE};
                border: none;
                border-radius: 20px;
                font-weight: 500;
                font-size: 14px;
                padding: 0px 20px;
            }}
            QPushButton:hover {{
                background: {SURFACE_CONTAINER_HIGHEST};
            }}
            QPushButton:pressed {{
                background: {PRIMARY};
                color: {ON_PRIMARY};
            }}
        """)
        back_btn.clicked.connect(back_callback)
        vbox.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Material Design 3 settings title
        settings_lbl = QLabel("Настройки")
        settings_lbl.setStyleSheet(f"""
            color: {ON_SURFACE};
            font-size: 24px;
            font-weight: 500;
            margin-left: 20px;
            margin-top: 8px;
            margin-bottom: 16px;
        """)
        vbox.addWidget(settings_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        # --- Material Design 3 audio devices dropdown ---
        devices = get_audio_lines()
        self.device_combo = QComboBox()
        self.device_combo.setStyleSheet(f"""
            QComboBox {{
                background: {SURFACE_CONTAINER_HIGH};
                color: {ON_SURFACE};
                border: 1px solid {SURFACE_VARIANT};
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 14px;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {PRIMARY};
            }}
            QComboBox:focus {{
                border-color: {PRIMARY};
                border-width: 2px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
        """)
        self.device_combo.setFixedWidth(300)
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


        # Добавляем отступ внизу
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
    """Material Design 3 folder selection field."""
    def __init__(self, label_text, initial_value="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE_CONTAINER_HIGH};
                border-radius: 16px;
                border: none;
            }}
        """)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(20, 12, 20, 12)
        hbox.setSpacing(16)
        
        self.label = QLabel(label_text)
        self.label.setStyleSheet(f"""
            color: {ON_SURFACE};
            font-size: 14px;
            font-weight: 500;
            min-width: 140px;
        """)
        
        self.lineedit = QLineEdit()
        self.lineedit.setText(initial_value)
        self.lineedit.setStyleSheet(f"""
            QLineEdit {{
                background: {SURFACE};
                color: {ON_SURFACE};
                border: 1px solid {SURFACE_VARIANT};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {PRIMARY};
                border-width: 2px;
            }}
        """)
        
        self.button = QPushButton("…")
        self.button.setFixedSize(40, 36)
        self.button.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE_VARIANT};
                color: {ON_SURFACE_VARIANT};
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 500;
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
    """Material Design 3 input container with label."""
    def __init__(self, label_text, widget, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE_CONTAINER_HIGH};
                border-radius: 16px;
                border: none;
            }}
        """)
        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(20, 12, 20, 12)
        hbox.setSpacing(16)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            color: {ON_SURFACE};
            font-size: 14px;
            font-weight: 500;
            min-width: 140px;
        """)
        hbox.addWidget(label)
        hbox.addWidget(widget, stretch=1)