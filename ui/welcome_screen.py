from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class WelcomeScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Welcome")
        self.setStyleSheet("background-color: #262255;")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()

        label = QLabel("Welcome!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-size: 28px; font-family: Arial;")
        layout.addWidget(label)

        next_btn = QPushButton("→")
        next_btn.setFixedSize(60, 40)
        next_btn.setStyleSheet("background-color: #ccc; font-size: 20px;")
        next_btn.clicked.connect(self.controller.showMusclePairs)
        layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        print("✅ WelcomeScreen initialized and visible.")

