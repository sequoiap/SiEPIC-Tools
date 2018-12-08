
import pya
from . import mpl

class CircuitAnalysisGUI():

    def __init__(self):
        import os
        mpl.plot()
        
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../files/circuit_analysis_gui.ui")
        print("Valid path:", os.path.isfile(path))
        ui_file = pya.QFile(path)
        ui_file.open(pya.QIODevice().ReadOnly)
        self.window = pya.QFormBuilder().load(ui_file, pya.Application.instance().main_window())
        ui_file.close

        self.window.findChild('ok').clicked(self.ok)
        self.window.findChild('cancel').clicked(self.close)
        self.clicked = True
        self.window.exec_()

    def close(self, val):
        self.clicked = False
        self.window.close()

    def ok(self, val):
        self.clicked = True
        self.window.close()
        
def circuit_analysis():
    gui = CircuitAnalysisGUI()