class Component():
    
    def __init__(self, id, label):
        self.deviceID = id
        self.label = label
        self.ports = []
        self.posx = None
        self.posy = None

    def printPorts(self):
        print("DEVICE ID:", self.deviceID, ", or", self.label, ", has", len(self.ports), "port(s).")
        for port in self.ports:
            print(port)