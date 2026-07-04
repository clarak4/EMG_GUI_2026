import os

os.environ.pop("QT_PLUGIN_PATH", None)
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)

import sys
import math
import serial
import threading
import time
from pathlib import Path

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QSizePolicy
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QTimer, QPoint, QLibraryInfo

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# from ui.circular_gauge import CircularGauge
from ui.data_analyzer import SessionAnalyzer
# from ui.circular_countdown import CircularCountdown


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


SERIAL_PORT = "/dev/cu.usbmodem3C8427C325202"
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
                print("RAW SERIAL:", line)
                if line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("sensor1:"):
                            self.reading1 = int(part.split(":")[1])
                        elif part.startswith("sensor2:"):
                            self.reading2 = int(part.split(":")[1])
                    print("Parsed:", self.reading1, self.reading2)
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
        home_icon = QPixmap(resource_path("assets/home_icon.png")).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio)
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

        top_bar.addWidget(home_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(stop_btn, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(top_bar)

        # Info Labels (Timer, Reps)
        self.timer_label = QLabel("Timer: 00:00")
        #self.rep_label = QLabel("Repetitions: 0")
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        #self.rep_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        # self.ratio_gauge = CircularGauge()
        # self.ratio_gauge.setMinimumSize(220, 220)

        # Live Bar Graph Setup
        self.bar_canvas = FigureCanvas(Figure(figsize=(3, 2)))
        self.bar_ax = self.bar_canvas.figure.add_subplot(111)

        # Match app background
        self.bar_canvas.figure.patch.set_facecolor("#2c265e")
        self.bar_ax.set_facecolor("#2c265e")

        self.bar_canvas.setMinimumSize(450, 300)

        training_row = QHBoxLayout()
        training_row.setContentsMargins(0, 0, 0, 0)
        training_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        training_row.addStretch()
        # training_row.addWidget(self.ratio_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        training_row.addWidget(self.bar_canvas, alignment=Qt.AlignmentFlag.AlignCenter)
        training_row.addStretch()

        training_container = QWidget()
        training_container.setFixedHeight(360)
        training_container.setLayout(training_row)

        main_layout.addWidget(training_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Matplotlib EMG Graph Setup
        self.canvas = FigureCanvas(Figure(figsize=(5, 4.2)))
        self.canvas.setMinimumHeight(270)

        # two stacked raw graphs
        self.ax_target = self.canvas.figure.add_subplot(211)
        self.ax_comp = self.canvas.figure.add_subplot(212, sharex=self.ax_target)

        self.ax_target.set_ylabel("Raw Target EMG\n(ADC counts)", fontsize=9, color="black")
        self.ax_comp.set_ylabel("Raw Compensation EMG\n(ADC counts)", fontsize=9, color="black")
        self.ax_comp.set_xlabel("Time (s)", fontsize=10, color="black")

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
        #value1 = abs(self.reader.reading1)
        #value2 = abs(self.reader.reading2)

        # Mock EMG data for testing raw graphs
        self.mock_time += 0.05

        value1 = int(600 + 400 * math.sin(2 * math.pi * 0.4 * self.mock_time))
        value2 = int(1800 + 1200 * math.sin(2 * math.pi * 0.25 * self.mock_time + 1))

        # keep values positive
        value1 = max(0, value1)
        value2 = max(0, value2)

    # For Debugging
        print("Target:", value1, "Compensation:", value2)
        print("UI values:", value1, value2)
    
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
        # self.ratio_gauge.setRatio(ratio)

        # Update live bar graph
        self.bar_ax.clear()

        self.bar_ax.set_facecolor("#2c265e")
        self.bar_canvas.figure.patch.set_facecolor("#2c265e")

        labels = ["Target", "Compensation"]
        
        values = [value1, value2]
        colors = ["#009E73", "#E69F00"]

        self.bar_ax.bar(labels, values, color=colors, edgecolor="black", linewidth=2)
    
        self.bar_ax.tick_params(axis="x", colors="white", labelsize=12)

        for spine in self.bar_ax.spines.values():
            spine.set_color("white")

        bar_ymax = max(value1, value2)
        bar_buffer = max(20, bar_ymax * 0.1)
        self.bar_ax.set_ylim(0, bar_ymax + bar_buffer)

        self.bar_ax.set_ylabel("")
        self.bar_ax.set_yticks([])

        # Give extra left margin so y-axis numbers are not cut off
        self.bar_canvas.figure.subplots_adjust(left=0.08, right=0.95, bottom=0.25, top=0.95)

        self.bar_canvas.draw()


        self.data_y1 = self.data_y1[1:] + [value1]
        self.data_y2 = self.data_y2[1:] + [value2]

        self.ax_target.clear()
        self.ax_comp.clear()

        # main curves
        self.ax_target.plot(self.data_x, self.data_y1, color="#009E73", linewidth=2.2)
        self.ax_comp.plot(self.data_x, self.data_y2, color="#E69F00", linewidth=2.2)

        # layered curves
        self.ax_target.plot(self.data_x, self.data_y2, color="#F6C36A", linewidth=1.5, alpha=0.35)
        self.ax_comp.plot(self.data_x, self.data_y1, color="#7BC8A4", linewidth=1.5, alpha=0.35)

        # separate y-axis scaling for target
        target_ymax = max(self.data_y1)
        target_buffer = max(20, target_ymax * 0.1)
        self.ax_target.set_ylim(0, target_ymax + target_buffer)

        # separate y-axis scaling for compensation
        comp_ymax = max(self.data_y2)
        comp_buffer = max(20, comp_ymax * 0.1)
        self.ax_comp.set_ylim(0, comp_ymax + comp_buffer)

        # labels
        self.ax_target.set_ylabel("Target\nADC counts", fontsize=9, color="black")
        self.ax_comp.set_ylabel("Compensation\nADC counts", fontsize=9, color="black")
        self.ax_comp.set_xlabel("Time (s)", fontsize=10, color="black")

        # titles
        self.ax_target.set_title("Target Muscle Raw EMG", fontsize=10)
        self.ax_comp.set_title("Compensation Muscle Raw EMG", fontsize=10)

        # styling
        for ax in [self.ax_target, self.ax_comp]:
            ax.tick_params(axis='x', colors='black', labelsize=8)
            ax.tick_params(axis='y', colors='black', labelsize=8)
            ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

        self.canvas.figure.subplots_adjust(left=0.10, right=0.98, top=0.90, bottom=0.18, hspace=0.65)
        self.canvas.draw()     


    # Cleanup + Exit
    def closeEvent(self, event):
        self.reader.stop()
        event.accept()

    def confirm_exit(self):
        reply = QMessageBox.question(
            self,
            "Exit to Home",
            "Are you sure you want to return to the home screen?\nYour EMG session will stop.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
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

