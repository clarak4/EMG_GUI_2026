from ui.muscle_pairs import MusclePairScreen
from ui.welcome_screen import WelcomeScreen
from ui.emg_instruction import EMGInstructionScreen
from ui.connect_instruction import ConnectInstructionScreen
from ui.collect_data import CollectDataWindow


class Controller:
    def __init__(self):
        self.welcome = WelcomeScreen(self)
        self.muscle_pairs = None
        self.instruction = None
        self.connect_instruction = None
        self.collect_data = None
        self.biofeedback_watch_status = "Unknown"

    def showWelcome(self):
        if self.muscle_pairs:
            self.muscle_pairs.close()
        if self.instruction:
            self.instruction.close()
        if self.connect_instruction:
            self.connect_instruction.close()
        if self.collect_data:
            self.collect_data.close()
        self.welcome.show()


    def showMusclePairs(self):
        if self.welcome:
            self.welcome.close()

        self.muscle_pairs = MusclePairScreen(self)
        self.muscle_pairs.show()



    def showInstruction(self, muscle_pair_tuple):
        self.selected_muscle_pair = muscle_pair_tuple  # a tuple like ("Biceps", "Triceps")
        self.muscle_pairs.close()
        self.instruction = EMGInstructionScreen(self, muscle_pair_tuple)
        self.instruction.show()


    def showConnectInstruction(self):
        if self.instruction:
            self.instruction.close()
        self.connect_instruction = ConnectInstructionScreen(self)
        self.connect_instruction.show()

    def setValue(self, value):
        self._value = value  # whatever internal variable stores the value
        self.update()        # trigger a repaint

    def showGraph(self):
        if self.instruction:
            self.instruction.close()
        self.collect_data = CollectDataWindow(self, self.selected_muscle_pair)
        self.collect_data.show()


