from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget, QSizePolicy
from style import *

class WindowControls(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        btn_minimize = QPushButton("−")
        btn_minimize.setFixedSize(40, 40)
        btn_minimize.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {ON_SURFACE};
                font-size: 16px;
                font-weight: 500;
                border: none;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_CONTAINER};
                color: {PRIMARY};
            }}
            QPushButton:pressed {{
                background: {PRIMARY};
                color: {ON_PRIMARY};
            }}
        """)
        btn_minimize.clicked.connect(main_window.showMinimized)

        btn_close = QPushButton("×")
        btn_close.setFixedSize(40, 40)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {ERROR};
                font-size: 18px;
                font-weight: 500;
                border: none;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background: {ERROR_CONTAINER};
                color: {ON_ERROR};
            }}
            QPushButton:pressed {{
                background: {ERROR};
                color: {ON_PRIMARY};
            }}
        """)
        btn_close.clicked.connect(main_window.close)

        self.layout.addWidget(spacer)
        self.layout.addWidget(btn_minimize)
        self.layout.addWidget(btn_close)
