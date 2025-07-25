from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QHBoxLayout, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class MusclePairScreen(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Muscle Pairs")
        self.setStyleSheet("background-color: #2c265e; color: white;")
        self.setFixedSize(800, 600)

        # --- Top Navigation Bar ---
        nav_bar = QHBoxLayout()

        home_btn = QPushButton()
        # Build correct absolute path to home_icon.png
        home_icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "home_icon.png")
        home_icon_raw = QPixmap(resource_path(home_icon_path))

        # Debug print if image fails
        if home_icon_raw.isNull():
            print("❗️ home_icon.png failed to load — check path:", home_icon_path)

        # Scale and assign
        home_icon = home_icon_raw.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        home_btn.setIcon(QIcon(home_icon))
        home_btn.setIconSize(home_icon.size())

        home_btn.setFixedSize(40, 40)
        home_btn.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #3a3472; }")
        home_btn.clicked.connect(self.controller.showWelcome)

        nav_bar.addWidget(home_btn, alignment=Qt.AlignLeft)

        # --- Title ---
        title = QLabel("Muscle Pairs :")
        title.setFont(QFont("Arial", 24))
        title.setAlignment(Qt.AlignCenter)

        # --- Legend ---
        legend_layout = QHBoxLayout()
        target_color = QLabel("Target")
        target_color.setStyleSheet("background-color: #D8FFFD; padding: 5px; color: black;")
        comp_color = QLabel("Compensation")
        comp_color.setStyleSheet("background-color: #7493A9; padding: 5px; color: black;")
        legend_layout.addStretch()
        legend_layout.addWidget(target_color)
        legend_layout.addSpacing(10)
        legend_layout.addWidget(comp_color)
        legend_layout.addStretch()

        # --- Muscle Pair Matrix ---
        matrix_container = QHBoxLayout()
        matrix_layout = QGridLayout()
        matrix_layout.setHorizontalSpacing(40)
        matrix_layout.setVerticalSpacing(10)

        pairs = [
            ("Infraspinatus", "Upper Trapezius"),
            ("Deep Abdominals; Transverse Abdominis; Obliques", "Erectors; Rectus Abdominis"),
            ("Gluteus Medius; Gluteus Maximus", "Hip Flexors"),
            ("Gluteus Medius", "TFL"),
            ("Vastus Medialis Obliquus", "Vastus Lateralis"),
            ("Peroneals", "Tibialis Posterior")
        ]

        header1 = QLabel("Agonist")
        header2 = QLabel("Antagonist")
        header1.setFont(QFont("Arial", 16, QFont.Bold))
        header2.setFont(QFont("Arial", 16, QFont.Bold))
        matrix_layout.addWidget(header1, 0, 0, alignment=Qt.AlignCenter)
        matrix_layout.addWidget(header2, 0, 1, alignment=Qt.AlignCenter)

        for i, (agonist, antagonist) in enumerate(pairs):
            agonist_lines = "\n".join([muscle.strip() for muscle in agonist.split(';')])
            antagonist_lines = "\n".join([muscle.strip() for muscle in antagonist.split(';')])

            full_btn = QPushButton()
            full_btn.setCursor(Qt.PointingHandCursor)
            full_btn.setMinimumHeight(60)
            full_btn.setMinimumWidth(700)
            full_btn.setStyleSheet("QPushButton { background-color: transparent; border: none; } QPushButton:hover { background-color: #3a3472; }")
            full_btn.clicked.connect(lambda _, pair=(agonist, antagonist): [
                self.controller.showInstruction(pair),
                self.close()
            ])

            row_layout = QHBoxLayout()

            agonist_label = QLabel(agonist_lines)
            agonist_label.setStyleSheet("background-color: #D8FFFD; padding: 4px; font-size: 12px; color: black; border: none;")
            agonist_label.setAlignment(Qt.AlignCenter)
            agonist_label.setWordWrap(True)
            agonist_label.setMinimumWidth(300)
            agonist_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            antagonist_label = QLabel(antagonist_lines)
            antagonist_label.setStyleSheet("background-color: #7493A9; padding: 4px; font-size: 12px; color: black; border: none;")
            antagonist_label.setAlignment(Qt.AlignCenter)
            antagonist_label.setWordWrap(True)
            antagonist_label.setMinimumWidth(300)
            antagonist_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            row_layout.addWidget(agonist_label)
            row_layout.addSpacing(20)
            row_layout.addWidget(antagonist_label)

            row_frame = QFrame()
            row_frame.setLayout(row_layout)
            full_btn.setLayout(row_layout)

            matrix_layout.addWidget(full_btn, i+1, 0, 1, 2)

        matrix_container.addStretch()
        matrix_container.addLayout(matrix_layout)
        matrix_container.addStretch()

        # --- Final Layout Assembly ---
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.addLayout(nav_bar)
        layout.addWidget(title)
        layout.addLayout(legend_layout)
        layout.addSpacing(10)
        layout.addLayout(matrix_container)

        # --- Bottom Navigation ---
        forward_btn = QPushButton("→")
        forward_btn.setFixedSize(40, 40)
        forward_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")

        back_btn = QPushButton("←")
        back_btn.setFixedSize(40, 40)
        back_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")
        back_btn.clicked.connect(self.controller.showWelcome)

        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(back_btn, alignment=Qt.AlignLeft)
        bottom_bar.addStretch()
        bottom_bar.addWidget(forward_btn, alignment=Qt.AlignRight)

        layout.addStretch()
        layout.addLayout(bottom_bar)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

