from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget, QSizePolicy

class WindowControls(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        btn_minimize = QPushButton("–")
        btn_minimize.setAccessibleName("minimizeWindow")
        btn_minimize.setFixedSize(32, 32)
        btn_minimize.setStyleSheet("""
            QPushButton {
                background: none;
                color: #AAB8CC;
                font-size: 18px;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: #293448;
                color: #55aaff;
            }
        """)
        btn_minimize.clicked.connect(main_window.showMinimized)

        btn_close = QPushButton("✕")
        btn_close.setAccessibleName("closeWindow")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet("""
            QPushButton {
                background: none;
                color: #AAB8CC;
                font-size: 18px;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: #E25454;
                color: white;
            }
        """)
        btn_close.clicked.connect(main_window.close)

        self.layout.addWidget(spacer)
        self.layout.addWidget(btn_minimize)
        self.layout.addWidget(btn_close)
