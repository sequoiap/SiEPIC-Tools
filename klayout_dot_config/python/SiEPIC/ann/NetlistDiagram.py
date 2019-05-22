import subprocess
import datetime
import os
import SiEPIC._globals as glob
from SiEPIC.ann.model import Component

class Parser():
    def __init__(self, filepath):
        self.componentList = []
        self.nextID = 0
        self.filepath = filepath

    def createComponent(self):
        pass

    def parseFile(self):
        infile = open(self.filepath)
        filelines = infile.readlines()
        for line in filelines:
            elements = line.split()
            if len(elements) > 0:
                if (".ends" in elements[0]):
                    break
                elif ("." in elements[0]) or ("*" in elements[0]):
                    continue
                else:
                    self.parseComponent(elements)
        
    def parseComponent(self, line):
        newComponent = Component(self.nextID, line[0])
        self.nextID += 1
        for item in line:
            if "N$" in item:
                port = str(item).replace("N$", '')
                newComponent.ports.append(int(port))
        indices = [line.index(i) for i in line if 'lay_x=' in i]
        if len(indices) > 0:
            newComponent.posx = float(line[indices[0]].replace('lay_x=',''))
        indices = [line.index(i) for i in line if 'lay_y=' in i]
        if len(indices) > 0:
            newComponent.posy = float(line[indices[0]].replace('lay_y=',''))
        self.componentList.append(newComponent)

    def getComponents(self):
        return self.componentList

    def getComponentCount(self):
        return len(self.componentList)
        
    def getExternals(self):
        x = -1
        externals = []
        found = False
        external_components = []
        while True:
            for component in self.componentList:
                for port in component.ports:
                    if(port == x):
                        found = True
                        externals.append(-x)
                        x -= 1
                        external_components.append(component)
            if(not found):
                break
            found = False
        return externals, external_components
            

class DiagramMaker():
    def __init__(self, componentList):
        self.componentList = componentList
        self.portList = []

    def connectPorts(self):
        devices = []
        x = 0
        while True:
            for component in self.componentList:
                if x in component.ports:
                    devices.append(component)
            if len(devices) == 2:
                self.portList.append((devices[0].deviceID, devices[1].deviceID))
                devices = []
                x += 1
            elif (len(devices) == 0):
                break
            else:
                raise RuntimeError('ERROR: Device pair not found.')

    def makeDiagram(self):
        from time import sleep
        import pygraphviz as pgv
        wd = os.getcwd()
        temppath = glob.TEMP_FOLDER
        os.chdir(temppath)
        G = pgv.AGraph(overlap='false', size="20,20", ratio='fill')
        for component in self.componentList:
            title = component.label
            # Find all ports that have external connections
            externals = [x for x in component.ports if x < 0 ]
            print(externals)
            if(len(externals) > 0):
                additional = "\nExternal port numbers: "
                for port in externals:
                    additional = additional + str(-port) + " "
                title += additional
            G.add_node(component.deviceID, shape='box', label=title)
        for connection in self.portList:
            x, y = connection
            G.add_edge(x, y)
        G.layout()
        G.draw('Schematic.png')
        sleep(0.2)
        os.chdir(wd)

    def runDiagramMaker(self):
        self.connectPorts()
        self.makeDiagram()

def demo():
    wd = os.getcwd()
    temppath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
    os.chdir(temppath)
    fname = 'singleComp0'
    netname = '_netlist' + fname + '.txt'
    test = Parser(netname)
    test.parseFile()
    print("# of Components:", test.getComponentCount())
    for component in test.componentList:
       component.printPorts()
    diagram = DiagramMaker(test.getComponents())
    diagram.runDiagramMaker()
    os.chdir(wd)
    
def getExternalPortList():
    wd = os.getcwd()
    temppath = glob.TEMP_FOLDER
    os.chdir(temppath)
    fname = 'singleComp0'
    netname = '_netlist' + fname + '.txt'
    netlist = Parser(netname)
    netlist.parseFile()
    externals, components = netlist.getExternals()
    os.chdir(wd)
    return externals, components

def run():
    wd = os.getcwd()
    temppath = glob.TEMP_FOLDER
    os.chdir(temppath)
    fname = 'singleComp0'
    netname = '_netlist' + fname + '.txt'
    netlist = Parser(netname)
    netlist.parseFile()
    diagram = DiagramMaker(netlist.getComponents())
    diagram.runDiagramMaker()
    os.chdir(wd)

if __name__ == "__main__":
    #demo()
    getExternalPortList()