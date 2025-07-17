from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QScrollArea,
    QHBoxLayout,
    QWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QTextCursor, QColor
from style import *
from log_buffer import LogBuffer
from .wave_widget import WaveWidget

class ConsolePanel(QFrame):
    def __init__(self, max_logs: int = 1000):
        super().__init__()
        self._buffer = LogBuffer(max_logs)
        self.setObjectName("right_frame")
        self.setFixedWidth(480)
        # Material Design 3 console panel
        self.setStyleSheet(f"""
            QFrame#right_frame {{
                background: {SURFACE_CONTAINER_HIGH};
                border-radius: 16px;
                border: none;
            }}
        """)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Material Design 3 console title
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(20, 20, 20, 12)

        console_title = QLabel("Console")
        console_title.setStyleSheet(f"""
            background: transparent;
            color: {ON_SURFACE};
            font-size: 20px;
            font-weight: 500;
        """)
        title_layout.addWidget(console_title)
        title_layout.addStretch()
        
        # Activity indicator with Material Design styling
        self.activity_indicator = QWidget()
        self.activity_indicator.setFixedSize(12, 12)
        self.activity_indicator.setStyleSheet(f"""
            background-color: {SUCCESS}; 
            border-radius: 6px;
            border: none;
        """)
        self.activity_indicator.setVisible(False)
        title_layout.addWidget(self.activity_indicator)

        vbox.addLayout(title_layout)
        
        # Wave animation container with Material Design styling
        wave_container = QHBoxLayout()
        wave_container.setContentsMargins(20, 0, 20, 12)
        
        self.wave_widget = WaveWidget()
        self.wave_widget.setFixedHeight(60)  # Smaller height for better aesthetics
        self.wave_widget.setStyleSheet(f"""
            border-radius: 12px;
            background-color: {SURFACE};
        """)
        wave_container.addWidget(self.wave_widget)
        
        vbox.addLayout(wave_container)
        self.wave_widget.setVisible(False) # Initially hidden

        # --- Material Design 3 log area ---
        self.console_box = QTextEdit()
        self.console_box.setReadOnly(True)
        self.console_box.setStyleSheet(f"""
            QTextEdit {{
                background: {SURFACE};
                color: {ON_SURFACE};
                border-radius: 12px;
                border: none;
                font-size: 13px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                line-height: 1.6;
                padding: 16px 20px;
                selection-background-color: {PRIMARY};
                selection-color: {ON_PRIMARY};
            }}
        """)

        # Material Design 3 scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
                margin: 0px 16px 16px 16px;
                border-radius: 12px;
            }}
        """)
        self.scroll_area.verticalScrollBar().setStyleSheet(SCROLLBAR_STYLE)
        self.scroll_area.setWidget(self.console_box)
        self.scroll_area.verticalScrollBar().setStyleSheet(SCROLLBAR_STYLE)
        vbox.addWidget(self.scroll_area)

        # Пример вывода лога при запуске
        self.insert_log([
            ("10:57:51", "INFO Initializing", "#4DC3F6"),
            ("10:57:52", "Started process proc...", "#4DC3F6"),
            ("10:57:52", "Initialiaisizing", "#4DC3F6"),
            ("10:57:53", "Started", "#4DC3F6"),
            ("10:57:53", "INFO Initialize", "#4DC3F6"),
            ("10:57:53", "INFO Finished proc...", "#4DC3F6"),
            ("10:57:53", "ERROR An unexpected", "#FF7043"),
            ("10:57:55", "error occurred", "#FF7043")
        ])

    def set_recording_state(self, is_recording):
        self.wave_widget.setVisible(is_recording)
        self.activity_indicator.setVisible(is_recording)
        if is_recording:
            self.wave_widget.start_animation()
        else:
            self.wave_widget.stop_animation()

    def insert_log(self, records):
        """Добавить записи в консоль с улучшенным форматированием."""
        lines = []
        for time, text, color in records:
            line = (
                f'<span style="color:{PRIMARY}; font-weight:500;">{time}</span> '
                f'<span style="color:{color}">{text}</span>'
            )
            lines.append(line)
        self._buffer.extend(lines)
        self.console_box.setHtml(self._buffer.render_html("<br>"))
        # Перемещаем курсор в конец и скроллим вниз
        cursor = self.console_box.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console_box.setTextCursor(cursor)
        self.console_box.ensureCursorVisible()
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(bar.maximum())
