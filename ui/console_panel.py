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
        self.setFixedWidth(440)
        # Скругление и фон у всего фрейма
        self.setStyleSheet(f"""
            QFrame#right_frame {{
                background: {CONSOLE_BG};
                border-radius: 20px;
            }}
        """)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Заголовок консоли
        console_title = QLabel("Console")
        console_title.setStyleSheet(f"""
            background: transparent;   /* важно! */
            color: {LABEL_TEXT};
            font-size: 18px;
            font-weight: bold;
            padding-left: 18px;
            padding-top: 16px;
            padding-bottom: 8px;
        """)
        vbox.addWidget(console_title)

        # --- Область с логами ---
        self.console_box = QTextEdit()
        self.console_box.setReadOnly(True)
        self.console_box.setStyleSheet(
            f"""
            background: {CONSOLE_BG};
            color: {CONSOLE_TEXT};
            border-radius: 12px;
            border: none;
            font-size:14px;
            margin-left:0px;
            margin-right:0px;
            padding-left:18px;
            padding-right:18px;
            """
        )

        # Оборачиваем QTextEdit в скролл, чтобы всегда был вертикальный скроллбар
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: transparent; border:none;")
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
