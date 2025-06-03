from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from style import *

class ConsolePanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("right_frame")
        self.setFixedWidth(440)
        # Скругление и фон у всего фрейма!
        self.setStyleSheet(f"""
            QFrame#right_frame {{
                background: {CONSOLE_BG};
                border-radius: 20px;
            }}
        """)
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Заголовок — на том же фоне, не делай ему свой border-radius!
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

        self.console_box = QTextEdit()
        self.console_box.setReadOnly(True)
        self.console_box.setStyleSheet(f"""
            background: transparent;  
            color: {CONSOLE_TEXT};
            border: none;
            border-radius: 0px;        
            font-size:14px;
            margin-left:18px;
            margin-right:18px;
        """)
        vbox.addWidget(self.console_box)

        self.console_box.setReadOnly(True)
        self.console_box.setStyleSheet(f"""
            background: {CONSOLE_BG};
            color: {CONSOLE_TEXT};
            border-radius: 12px;
            font-size:14px;
            margin-left:18px;
            margin-right:18px;
        """)
        vbox.addWidget(self.console_box)

        # >>> Вот пример вывода лога:
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
        for time, text, color in records:
            self.console_box.append(f'<span style="color:#3FC7F3">{time}</span> '
                                   f'<span style="color:{color}">{text}</span>')
