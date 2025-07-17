from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor
from style import *
from ui.window_controls import WindowControls
from ui.left_panel import LeftPanel
from ui.console_panel import ConsolePanel
import ctypes
import ctypes.wintypes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # --- Параметры главного окна ---
        self.setWindowTitle("SoundDraftico")
        self.setFixedSize(1200, 600)
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {BACKGROUND};
                border-radius: 16px;
            }}
        """)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Material Design elevation shadow
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.show()
        hwnd = int(self.winId())
        self.set_rounded_corners(hwnd)

        # --- Центральный виджет и основной layout ---
        central = QWidget()
        central.setStyleSheet(f"background: {BACKGROUND}; border-radius: 12px;")
        vertical_layout = QVBoxLayout(central)
        vertical_layout.setContentsMargins(16, 16, 16, 16)
        vertical_layout.setSpacing(16)

        # Header с кнопками
        self.window_controls = WindowControls(self)
        vertical_layout.addLayout(self.window_controls.layout)

        # --- Основной горизонтальный layout (контент) ---
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)
        vertical_layout.addLayout(main_layout)

        self.console_panel = ConsolePanel()

        # --- Левая и правая панели ---
        self.left_panel = LeftPanel(console_panel=self.console_panel)
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.console_panel)
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(central)

    def insert_log(self, records):
        """Передать список записей в консольный виджет."""
        self.console_panel.insert_log(records)

    def mousePressEvent(self, event):
        # Запоминаем позицию мыши при нажатии, чтобы можно было перемещать окно
        if event.button() == Qt.MouseButton.LeftButton:
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        # Реализуем перетаскивание окна за любую область
        if hasattr(self, '_old_pos') and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = event.globalPosition().toPoint()

    def set_rounded_corners(self, hwnd):
        """Задаём окну скругленные углы через WinAPI."""
        DWMWCP_ROUND = 2
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.wintypes.HWND(hwnd),
            ctypes.wintypes.DWORD(DWMWA_WINDOW_CORNER_PREFERENCE),
            ctypes.byref(ctypes.wintypes.DWORD(DWMWCP_ROUND)),
            ctypes.sizeof(ctypes.wintypes.DWORD)
        )
