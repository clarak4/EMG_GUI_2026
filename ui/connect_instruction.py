from PyQt5.QtWidgets import QWidget, QMessageBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class ConnectInstructionScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Connect Sensors")
        self.setStyleSheet("background-color: #2c265e; color: white;")
        self.setFixedSize(800, 600)

        # --- Top Navigation ---
        top_bar = QHBoxLayout()

        home_btn = QPushButton()
        home_icon = QPixmap(resource_path("assets/home_icon.png")).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        home_btn.setIcon(QIcon(home_icon))
        home_btn.setIconSize(home_icon.size())
        home_btn.setFixedSize(40, 40)
        home_btn.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #3a3472; }")
        home_btn.clicked.connect(self.controller.showWelcome)

        top_bar.addWidget(home_btn, alignment=Qt.AlignLeft)


        # --- Message ---
        message = QLabel("Connect when you are ready!")
        message.setFont(QFont("Arial", 20))
        message.setAlignment(Qt.AlignCenter)

        # --- Connect Button ---
        connect_btn = QPushButton("Connect")
        connect_btn.setStyleSheet("""
        QPushButton {
            background-color: #4e4a89;
            font-size: 16px;
            padding: 10px;
            color: white;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #615cb2;
        }
    """)
        connect_btn.clicked.connect(self.ask_biofeedback_preference)

        # --- Bottom Navigation ---
        bottom_bar = QHBoxLayout()

        back_btn = QPushButton("←")
        back_btn.setFixedSize(40, 40)
        back_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")
        back_btn.clicked.connect(self.controller.showInstruction)

        forward_btn = QPushButton("→")
        forward_btn.setFixedSize(40, 40)
        forward_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")
        forward_btn.clicked.connect(self.controller.showGraph)

        bottom_bar.addWidget(back_btn, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        bottom_bar.addWidget(forward_btn, alignment=Qt.AlignRight)


        # --- Layout ---
        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addStretch()
        layout.addWidget(message)
        layout.addWidget(connect_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addLayout(bottom_bar)

        self.setLayout(layout)

    def ask_biofeedback_preference(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Biofeedback Preference")
        msg_box.setText("Will you be watching the live biofeedback?")
        msg_box.setIcon(QMessageBox.Question)

        yes_button = msg_box.addButton("Yes", QMessageBox.YesRole)
        no_button = msg_box.addButton("No", QMessageBox.NoRole)
        msg_box.setDefaultButton(yes_button)

        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            self.controller.biofeedback_watch_status = "Yes"
        else:
            self.controller.biofeedback_watch_status = "No"

        self.controller.showGraph()
