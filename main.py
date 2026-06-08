import sys
from PySide6.QtWidgets import QApplication
from controller import Controller

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    controller.showWelcome()
    sys.exit(app.exec())