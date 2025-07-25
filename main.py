from PyQt5.QtWidgets import QApplication
from controller import Controller
import fpdf
import sys

global_controller = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    global_controller = Controller()
    global_controller.showWelcome()
    #Keeps app running
    sys.exit(app.exec_())
