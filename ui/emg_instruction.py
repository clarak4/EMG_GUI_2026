from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


class EMGInstructionScreen(QWidget):
    def __init__(self, controller, muscle_pair_name):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("EMG Placement")
        self.setStyleSheet("background-color: #2c265e; color: white;")
        self.setFixedSize(800, 600)

        self.muscle_pair = muscle_pair_name

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


        # --- Title ---
        title = QLabel("Wipe muscle areas identified below with alcohol before attaching sensors")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignCenter)

        # --- Images and Labels ---
        img_layout = QHBoxLayout()

        image1 = QLabel()
        image2 = QLabel()

        print("muscle_pair received:", self.muscle_pair)
        print("type:", type(self.muscle_pair))
        
        target, comp = self.muscle_pair  # ✅ unpack the tuple

        if (target, comp) == ("Infraspinatus", "Upper Trapezius"):
            img1_path = "assets/infraspinatus.jpg"
            img2_path = "assets/uppertrap.jpg"

        elif (target, comp) == ("Deep Abdominals; Transverse Abdominis; Obliques", "Erectors; Rectus Abdominis"):
            img1_path = "assets/obliques.jpg"
            img2_path = "assets/rectusab.jpg"

        elif (target, comp) == ("Gluteus Medius; Gluteus Maximus", "Hip Flexors"):
            img1_path = "assets/glute.jpg"
            img2_path = "assets/hipflexor.jpg"

        elif (target, comp) == ("Gluteus Medius", "TFL"):
            img1_path = "assets/glutemed.jpg"
            img2_path = "assets/tfl.jpg"

        elif (target, comp) == ("Vastus Medialis Obliquus", "Vastus Lateralis"):
            img1_path = "assets/vmo.jpg"
            img2_path = "assets/vastuslat.jpg"

        elif (target, comp) == ("Peroneals", "Tibialis Posterior"):
            img1_path = "assets/peroneals.jpg"
            img2_path = "assets/tibialispost.jpg"

        else:
            img1_path = "assets/default1.jpg"
            img2_path = "assets/default2.jpg"

        path1 = resource_path(img1_path)
        path2 = resource_path(img2_path)

        pixmap1 = QPixmap(path1)
        pixmap2 = QPixmap(path2)

        image1.setAlignment(Qt.AlignCenter)
        image2.setAlignment(Qt.AlignCenter)

        image1.setStyleSheet("background-color: transparent;")
        image2.setStyleSheet("background-color: transparent;")

        image1.setFixedSize(300, 300)
        image2.setFixedSize(300, 300)

        image1.setScaledContents(False)
        image2.setScaledContents(False)

        image1.setPixmap(
            pixmap1.scaled(
                image1.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        image2.setPixmap(
            pixmap2.scaled(
                image2.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        img_layout.addWidget(image1)
        img_layout.addSpacing(50)
        img_layout.addWidget(image2)
        
        # --- Attach Labels ---
        label_layout = QHBoxLayout()
        label1 = QLabel("Attach Sensor 1")
        label2 = QLabel("Attach Sensor 2")
        label1.setAlignment(Qt.AlignCenter)
        label2.setAlignment(Qt.AlignCenter)
        label1.setFont(QFont("Arial", 14))
        label2.setFont(QFont("Arial", 14))

        label_layout.addStretch()
        label_layout.addWidget(label1)
        label_layout.addSpacing(150)
        label_layout.addWidget(label2)
        label_layout.addStretch()

        # --- Bottom Navigation ---
        forward_btn = QPushButton("→")
        forward_btn.setFixedSize(40, 40)
        forward_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")
        forward_btn.clicked.connect(self.controller.showConnectInstruction)

        back_btn = QPushButton("←")
        back_btn.setFixedSize(40, 40)
        back_btn.setStyleSheet("QPushButton { background-color: transparent; font-size: 18px; color: white; border: none; } QPushButton:hover { background-color: #3a3472; }")
        back_btn.clicked.connect(self.controller.showMusclePairs)

        # Citation label (centered between arrows)
        source_label = QLabel("Image source: Innerbody.com (muscle anatomy - musfov.html)")
        source_label.setFont(QFont("Arial", 9))
        source_label.setStyleSheet("color: #cccccc;")
        source_label.setAlignment(Qt.AlignCenter)

        bottom_bar = QHBoxLayout()
        
        # Add widgets in row: ←   [citation]   →
        bottom_bar.addWidget(back_btn, alignment=Qt.AlignLeft)
        bottom_bar.addStretch(1)
        bottom_bar.addWidget(source_label, alignment=Qt.AlignCenter)
        bottom_bar.addStretch(1)
        bottom_bar.addWidget(forward_btn, alignment=Qt.AlignRight)

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_bar)
        main_layout.addWidget(title, alignment=Qt.AlignCenter)
        main_layout.addSpacing(20)
        # --- Wrap image layout in a widget ---
        img_container = QWidget()
        img_container.setLayout(img_layout)
        img_container.setContentsMargins(0, 0, 0, 0)

        # --- Combine images + labels into one vertical layout ---
        image_block = QVBoxLayout()
        image_block.setAlignment(Qt.AlignCenter)
        image_block.addWidget(img_container, alignment=Qt.AlignCenter)
        image_block.addSpacing(10)
        image_block.addLayout(label_layout)

        # --- Add to main layout ---
        main_layout.addLayout(image_block)
        main_layout.addStretch()
        main_layout.addLayout(bottom_bar)

        self.setLayout(main_layout)