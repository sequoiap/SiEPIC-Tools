import subprocess
import datetime
import os

class Cell():
    def __init__(self, id, label):
        self.deviceID = id
        self.label = label
        self.ports = []

    def printPorts(self):
        print("DEVICE ID:", self.deviceID, ", or", self.label, ", has", len(self.ports), "port(s).")
        for port in self.ports:
            print(port)

class Parser():
    def __init__(self, filepath):
        self.cellList = []
        self.nextID = 0
        self.filepath = filepath

    def createCell(self):
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
                    self.parseCell(elements)
        
    def parseCell(self, line):
        newCell = Cell(self.nextID, line[0])
        self.nextID += 1
        for item in line:
            if "N$" in item:
                port = str(item).replace("N$", '')
                newCell.ports.append(int(port))
        self.cellList.append(newCell)

    def getCells(self):
        return self.cellList

    def getCellCount(self):
        return len(self.cellList)
        
    def getExternals(self):
        x = -1
        externals = []
        found = False
        while True:
            for cell in self.cellList:
                for port in cell.ports:
                    if(port == x):
                        found = True
                        externals.append(-x)
                        x -= 1
            if(not found):
                break
            found = False
        return externals
            

class DiagramMaker():
    def __init__(self, cellList):
        self.cellList = cellList
        self.portList = []
        # time = str(datetime.datetime.now())
        # time = time.replace(' ','_')
        # time = time.replace(':','.')
        # self.filename = "diagram_" + time + ".diag"

    def connectPorts(self):
        devices = []
        x = 0
        while True:
            for cell in self.cellList:
                if x in cell.ports:
                    devices.append(cell)
            if len(devices) == 2:
                self.portList.append((devices[0].deviceID, devices[1].deviceID))
                devices = []
                x += 1
            elif (len(devices) == 0):
                break
            else:
                raise RuntimeError('ERROR: Device pair not found.')
        # devices = []
        # maximum = 0
        # for cell in self.cellList:
        #     if maximum < max(cell.ports):
        #         maximum = max(cell.ports)
        # for x in range(maximum + 1):
        #     for cell in self.cellList:
        #         if x in cell.ports:
        #             devices.append(cell)
        #     self.portList.append((devices[0].deviceID, devices[1].deviceID))
        #     devices = []

    def makeDiagram(self):
        from time import sleep
        import pygraphviz as pgv
        wd = os.getcwd()
        temppath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
        os.chdir(temppath)
        G = pgv.AGraph(overlap='false', size="20,20", ratio='fill')
        for cell in self.cellList:
            title = cell.label
            # Find all ports that have external connections
            externals = [x for x in cell.ports if x < 0 ]
            print(externals)
            if(len(externals) > 0):
                additional = "\nExternal port numbers: "
                for port in externals:
                    additional = additional + str(-port) + " "
                title += additional
            G.add_node(cell.deviceID, shape='box', label=title)
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
    print("# of Cells:", test.getCellCount())
    for cell in test.cellList:
       cell.printPorts()
    diagram = DiagramMaker(test.getCells())
    diagram.runDiagramMaker()
    os.chdir(wd)
    
def getExternalPortList():
    wd = os.getcwd()
    temppath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
    os.chdir(temppath)
    fname = 'singleComp0'
    netname = '_netlist' + fname + '.txt'
    netlist = Parser(netname)
    netlist.parseFile()
    externals = netlist.getExternals()
    os.chdir(wd)
    return externals

def run():
    wd = os.getcwd()
    temppath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
    os.chdir(temppath)
    fname = 'singleComp0'
    netname = '_netlist' + fname + '.txt'
    netlist = Parser(netname)
    netlist.parseFile()
    diagram = DiagramMaker(netlist.getCells())
    diagram.runDiagramMaker()
    os.chdir(wd)

if __name__ == "__main__":
    #demo()
    getExternalPortList()