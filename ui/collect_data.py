from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QSizePolicy
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt, QTimer, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ui.circular_gauge import CircularGauge
from ui.data_analyzer import SessionAnalyzer
#from ui.circular_countdown import CircularCountdown
from pathlib import Path
import math
#import random #for mock EMG signals
import serial
import threading
import time
import os
import sys

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


SERIAL_PORT = '/dev/cu.usbmodem1101'
BAUD_RATE = 115200
# PHASES = [
#     ("ECCENTRIC", 4, "#E69F00"),
#     ("HOLD", 2, "#999999"),
#     ("CONCENTRIC", 4, "#009E73"),
#     ("HOLD", 2, "#999999")
# ]


# EMG Serial Reader
class EMGReader:
    def __init__(self):
        self.reading1 = 0
        self.reading2 = 0
        self.running = False
        self.ser = None
        self.thread = None

    def start(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
            self.running = True
            self.thread = threading.Thread(target=self.read_loop)
            self.thread.start()
        except Exception as e:
            print("Serial connection failed:", e)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.ser:
            self.ser.close()

    def read_loop(self):
        while self.running:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("sensor1:"):
                            self.reading1 = int(part.split(":")[1])
                        elif part.startswith("sensor2:"):
                            self.reading2 = int(part.split(":")[1])
            except Exception as e:
                print("Read error:", e)


# Main Widget Class
class CollectDataWindow(QWidget):
    def __init__(self, controller, muscle_pair_name):
        super().__init__()
        self.controller = controller
        self.muscle_pair_name = muscle_pair_name
        target_muscle, comp_muscle = self.muscle_pair_name

        # Timer State Variables
        self.elapsed_seconds = 0
        #self.current_phase_index = 0
        #self.phase_remaining = PHASES[0][1]
        #self.repetitions = 0
        self.is_running = False
        self.mock_time = 0  # Used for generating smooth mock EMG waves

        # EMG Reader Init
        self.reader = EMGReader()
        self.reader.start()

        # Window Settings
        self.setWindowTitle("Live EMG Feedback")
        self.setStyleSheet("background-color: #2c265e; color: white;")
        self.setFixedSize(1000, 720)
        main_layout = QVBoxLayout(self)

        # Top Control Bar (Home + Stop)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        home_btn = QPushButton()
        home_icon = QPixmap(resource_path("assets/home_icon.png")).scaled(24, 24, Qt.KeepAspectRatio)
        home_btn.setIcon(QIcon(home_icon))
        home_btn.setIconSize(home_icon.size())
        home_btn.setFixedSize(40, 40)
        home_btn.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background-color: #3a3472; }")
        home_btn.clicked.connect(self.controller.showWelcome)

        stop_btn = QPushButton("Stop")
        stop_btn.setFixedSize(80, 32)
        stop_btn.setStyleSheet("QPushButton { background-color: #D8FFFD; color: black; } QPushButton:hover { background-color: #a7f7f5; }")
        stop_btn.clicked.connect(self.stop_collection)
        stop_btn.clicked.connect(self.stop_training)

        top_bar.addWidget(home_btn, alignment=Qt.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(stop_btn, alignment=Qt.AlignRight)
        main_layout.addLayout(top_bar)

        # Info Labels (Timer, Reps)
        self.timer_label = QLabel("Timer: 00:00")
        #self.rep_label = QLabel("Repetitions: 0")
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        #self.rep_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.timer_label)
        #info_layout.addWidget(self.rep_label)
        main_layout.addLayout(info_layout)

        # # Phase Label & Circular Timer
        # self.phase_label = QLabel("ECCENTRIC")
        # font = QFont("Arial", 20)
        # font.setBold(True)
        # self.phase_label.setFont(font)
        # self.phase_label.setStyleSheet(f"color: {PHASES[0][2]};")

        # self.circular_timer = CircularCountdown(duration_seconds=PHASES[0][1], color=PHASES[0][2])

        # Training Visualization: Circular Gauge
        self.ratio_gauge = CircularGauge()
        self.ratio_gauge.setMinimumSize(220, 220)

        training_row = QHBoxLayout()
        training_row.setContentsMargins(0, 0, 0, 0)
        training_row.setAlignment(Qt.AlignCenter)

        training_row.addStretch(1)
        training_row.addWidget(self.ratio_gauge, alignment=Qt.AlignCenter)
        training_row.addStretch(1)

        training_container = QWidget()
        training_container.setFixedHeight(320)
        training_container.setLayout(training_row)

        main_layout.addWidget(training_container)

        # Matplotlib EMG Graph Setup
        self.canvas = FigureCanvas(Figure(figsize=(5, 2)))
        
        # remove for cleanliness
        self.ax = self.canvas.figure.add_subplot(111)
        # self.ax.set_ylim(0, 1023)

        self.ax.set_xlabel("Time (s)", fontsize=12, color="black", labelpad=10)
        self.ax.set_ylabel("EMG Amplitude (mV)", fontsize=12, color="black", labelpad=10)

        self.data_x = list(range(100))
        self.data_y1 = [0]*100
        self.data_y2 = [0]*100

        graph_container = QVBoxLayout()
        graph_container.addWidget(self.canvas)
        main_layout.addLayout(graph_container)

        # Timer Logic
        self.total_timer = QTimer()
        self.total_timer.timeout.connect(self.update_total_time)
        # self.phase_timer = QTimer()
        # self.phase_timer.timeout.connect(self.update_phase)
        # self.current_phase_index = 0
        # self.phase_remaining = PHASES[0][1]
        # self.repetitions = 0
        self.is_running = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(50)
        # self.circular_timer.start()
        self.start_training()

    # Timer + Phase Logic
    def start_training(self):
        if not self.is_running:
            self.is_running = True
            self.total_timer.start(1000)
            #self.phase_timer.start(1000)

    def update_total_time(self):
        self.elapsed_seconds += 1
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        self.timer_label.setText(f"Timer: {minutes:02}:{seconds:02}")

    # def update_phase(self):
    #     phase, duration, color = PHASES[self.current_phase_index]
    #     self.phase_label.setText(phase)
    #     self.phase_label.setStyleSheet(f"color: {color};")
    #     self.circular_timer.start(duration=self.phase_remaining, color=color)

    #     if self.phase_remaining == 0:
    #         self.current_phase_index = (self.current_phase_index + 1) % len(PHASES)
    #         self.phase_remaining = PHASES[self.current_phase_index][1]
    #         if self.current_phase_index == 0:
    #             self.repetitions += 1
    #             self.rep_label.setText(f"Repetitions: {self.repetitions}")
    #     else:
    #         self.phase_remaining -= 1

    # UI Update Loop
    def update_ui(self):
        value1 = abs(self.reader.reading1)
        value2 = abs(self.reader.reading2)
    
    # Uncomment below for realistic mock EMG wave signals
    # self.mock_time += 0.05  # Time step (every 50ms)
    #
    # # Target muscle (Sensor 1): sine wave + jitter
    # value1 = int(
    #     500 + 300 * math.sin(2 * math.pi * 0.5 * self.mock_time) + random.uniform(-50, 50)
    # )
    #
    # # Compensation muscle (Sensor 2): cosine wave with offset + jitter
    # value2 = int(
    #     300 + 200 * math.cos(2 * math.pi * 0.3 * self.mock_time + 1) + random.uniform(-40, 40)
    # )
    #
    # # Clamp to safe range (0–1023)
    # value1 = max(0, min(1023, value1))
    # value2 = max(0, min(1023, value2))

        ratio = value1 / (value1 + value2 + 1e-5)
        self.ratio_gauge.setRatio(ratio)

        self.data_y1 = self.data_y1[1:] + [value1]
        self.data_y2 = self.data_y2[1:] + [value2]

        self.ax.clear()
        self.ax.plot(self.data_x, self.data_y1, label="Target", color="#009E73", linewidth=2.5)
        self.ax.plot(self.data_x, self.data_y2, label="Compensation", color="#E69F00", linewidth=2.5)

        # fixed limites for y-axis
        # self.ax.set_ylim(0, 1023)
        
        # Y-axis bound: clamps lower bound to 0
        ymax = max(max(self.data_y1), max(self.data_y2))
        buffer = max(20, ymax * 0.1)
        self.ax.set_ylim(0, ymax + buffer)


        self.ax.set_xlabel("Time (s)", fontsize=12, color="black", labelpad=10)
        self.ax.set_ylabel("EMG Amplitude (mV)", fontsize=12, color="black", labelpad=10)
        self.ax.tick_params(axis='x', colors='black')
        self.ax.tick_params(axis='y', colors='black')
        self.ax.xaxis.label.set_color('black')
        self.ax.yaxis.label.set_color('black')
        self.ax.legend()
        self.canvas.draw()
        self.canvas.figure.subplots_adjust(top=0.88, bottom=0.30)
        self.ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
        
        print(f"Ratio: {ratio:.2f}")


    # Cleanup + Exit
    def closeEvent(self, event):
        self.reader.stop()
        event.accept()

    def confirm_exit(self):
        reply = QMessageBox.question(
            self,
            "Exit to Home",
            "Are you sure you want to return to the home screen?\nYour EMG session will stop.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.reader.stop()
            self.controller.showWelcome()
            self.close()

    def stop_training(self):
        self.total_timer.stop()
        #self.phase_timer.stop()
        self.is_running = False

    # Stop + Save Routine
    def stop_collection(self):
        self.timer.stop()
        print("⛔️ Data collection stopped.")

        session_data = {
            'target_muscle': self.data_y1,
            'comp_muscle': self.data_y2
        }
        mvic_values = {'target_muscle': 800, 'comp_muscle': 700}
        thresholds = {'target_muscle': 500, 'comp_muscle': 450}

        reply = QMessageBox.question(
            self,
            "Save Report?",
            "Do you want to save the summary report as a PDF?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            downloads_path = str(Path.home() / "Downloads")
            file_path = os.path.join(downloads_path, "session_summary.pdf")

            minutes = self.elapsed_seconds // 60
            seconds = self.elapsed_seconds % 60
            formatted_time = f"{minutes:02}:{seconds:02}"
            
            analyzer = SessionAnalyzer(
                data=session_data,
                duration=formatted_time,
                repetitions=self.repetitions,
                biofeedback_response=self.controller.biofeedback_watch_status  # Pass the response!
            )
            analyzer.export_pdf(file_path)

            QMessageBox.information(self, "Saved", f"📄 Summary saved as PDF in Downloads folder.")

        self.reader.stop()
        self.controller.showWelcome()
        self.close()

