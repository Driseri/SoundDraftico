from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QTimer
import numpy as np

class WaveWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.amplitudes = np.zeros(100)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_wave)
        self.phase = 0

    def start_animation(self):
        self.timer.start(50)  # Update every 50 ms

    def stop_animation(self):
        self.timer.stop()
        self.amplitudes.fill(0)
        self.update()

    def update_wave(self):
        # Simulate wave effect
        self.phase += 0.5
        t = np.linspace(0, 2 * np.pi, 100)
        wave = np.sin(t + self.phase) * np.sin(t * 5 + self.phase / 3) * 20 + 50
        self.amplitudes = np.roll(self.amplitudes, -1)
        self.amplitudes[-1] = np.random.rand() * wave[-1]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1C1B1F"))

        pen = QPen(QColor("#6750A4"), 2)
        painter.setPen(pen)

        path = self.create_wave_path()
        painter.drawPath(path)

    def create_wave_path(self):
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        if not self.amplitudes.any():
            return path

        w = self.width()
        h = self.height()
        points = np.column_stack((np.linspace(0, w, len(self.amplitudes)), h / 2 + self.amplitudes))
        path.moveTo(points[0, 0], points[0, 1])
        for i in range(len(points) - 1):
            cx1 = (points[i, 0] + points[i+1, 0]) / 2
            cy1 = points[i, 1]
            cx2 = (points[i, 0] + points[i+1, 0]) / 2
            cy2 = points[i+1, 1]
            path.cubicTo(cx1, cy1, cx2, cy2, points[i+1, 0], points[i+1, 1])
        return path