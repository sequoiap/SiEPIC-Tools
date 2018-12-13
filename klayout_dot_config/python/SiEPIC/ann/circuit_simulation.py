
import pya
import os
#from . import mpl

class CircuitAnalysisGUI():

    def __init__(self):
        #mpl.plot()
        
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../files/circuit_analysis_gui.ui")
        ui_file = pya.QFile(path)
        ui_file.open(pya.QIODevice().ReadOnly)
        self.window = pya.QFormBuilder().load(ui_file, pya.Application.instance().main_window())
        ui_file.close

        self.window.findChild('ok').clicked(self.ok)
        self.window.findChild('cancel').clicked(self.close)
        self.updatefig1()
        self.updatefig2()
        self.updatecircuit()
        self.clicked = True
        self.window.exec_()

    def close(self, val):
        self.clicked = False
        self.window.close()

    def ok(self, val):
        self.clicked = True
        self.window.close()
        
    def updatefig1(self):
        img = pya.QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp/mag.png"))
        self.window.findChild('fig1').setPixmap(img.scaled(500, 300))
    
    def updatefig2(self):
        img = pya.QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp/phase.png"))
        self.window.findChild('fig2').setPixmap(img.scaled(500, 300))
    
    def updatecircuit(self):
        img = pya.QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp/circuit.png"))
        self.window.findChild('schematic').setPixmap(img.scaled(400, 600))
        
def circuit_analysis():
    gui = CircuitAnalysisGUI()
    
if __name__ == "__main__":
    circuit_analysis()