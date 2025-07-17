from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from style import *
from log_buffer import LogBuffer

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
        console_title = QLabel("Console")
        console_title.setStyleSheet(f"""
            background: transparent;
            color: {ON_SURFACE};
            font-size: 20px;
            font-weight: 500;
            padding-left: 20px;
            padding-top: 20px;
            padding-bottom: 12px;
        """)
        vbox.addWidget(console_title)

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
                line-height: 1.4;
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

    def insert_log(self, records):
        """Добавить записи в консоль."""
        lines = []
        for time, text, color in records:
            line = (
                f'<span style="color:#3FC7F3">{time}</span>'
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
