from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QRectF, QTimer, Qt
from PySide6.QtGui import QPainter, QPen, QFont, QColor
import math

class CircularCountdown(QWidget):
    def __init__(self, duration_seconds=10, color="#E69F00", parent=None):
        super().__init__(parent)
        self.duration = duration_seconds
        self.remaining = duration_seconds
        self.color = QColor(color)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.setMinimumSize(150, 150)

    def start(self, duration=None, color=None):
        if duration:
            self.duration = duration
            self.remaining = duration
        if color:
            self.color = QColor(color)
        self.remaining = self.duration
        self.timer.start(1000)
        self.update()

    def stop(self):
        self.timer.stop()

    def update_timer(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = QRectF(self.rect().adjusted(10, 10, -10, -10))

        # Draw background circle
        pen = QPen(Qt.gray, 12)
        painter.setPen(pen)
        painter.drawEllipse(rect)

        # Draw arc
        pen.setColor(self.color)
        painter.setPen(pen)
        angle_span = 360 * (self.remaining / self.duration)
        painter.drawArc(rect, 90 * 16, int(-angle_span * 16))
    
        # Draw text
        painter.setPen(Qt.white)
        font = QFont("Arial", 28, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, str(self.remaining))
