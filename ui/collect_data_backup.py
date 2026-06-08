from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random


class CollectDataWindow(QWidget):
   def __init__(self, controller):
       super().__init__()
       self.controller = controller
       self.setWindowTitle("Live EMG Feedback")
       self.setStyleSheet("background-color: #2c265e; color: white;")
       self.setFixedSize(800, 600)


       # --- Top Navigation ---
       top_bar = QHBoxLayout()


       home_btn = QPushButton()
       home_icon = QPixmap("assets/home_icon.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
       home_btn.setIcon(QIcon(home_icon))
       home_btn.setIconSize(home_icon.size())
       home_btn.setFixedSize(40, 40)
       home_btn.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #3a3472; }")
       home_btn.clicked.connect(self.controller.showWelcome)


       top_bar.addWidget(home_btn, alignment=Qt.AlignLeft)


       # --- Title ---
       title = QLabel("Real-time EMG Feedback")
       title.setFont(QFont("Arial", 20))
       title.setAlignment(Qt.AlignCenter)


       # --- Graph Setup ---
       self.figure = Figure()
       self.canvas = FigureCanvas(self.figure)
       self.ax = self.figure.add_subplot(111)
       self.ax.set_title("EMG Signal")
       self.ax.set_xlabel("Time")
       self.ax.set_ylabel("Voltage (mV)")


       # --- Placeholder: Random data (you can replace with serial input from EMG) ---
       self.ax.plot([random.uniform(0, 1) for _ in range(100)])


       # --- Bottom Navigation ---
       forward_btn = QPushButton("→")
       forward_btn.setFixedSize(40, 40)
       forward_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")
       forward_btn.clicked.connect(lambda: print("Next step not defined"))
       back_btn = QPushButton("←")
       back_btn.setFixedSize(40, 40)
       back_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")
       back_btn.clicked.connect(self.controller.showConnectInstruction)


       bottom_bar = QHBoxLayout()
       bottom_bar.addWidget(back_btn, alignment=Qt.AlignLeft)
       bottom_bar.addStretch()
       bottom_bar.addWidget(forward_btn, alignment=Qt.AlignRight)


       # --- Layout ---
       layout = QVBoxLayout()
       layout.setContentsMargins(20, 10, 20, 10)
       layout.addLayout(top_bar)
       layout.addWidget(title)
       layout.addWidget(self.canvas)
       layout.addStretch()
       layout.addLayout(bottom_bar)


       self.setLayout(layout)


