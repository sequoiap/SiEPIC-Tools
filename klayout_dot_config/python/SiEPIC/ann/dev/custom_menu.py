import tkinter as tk

class MenuItems:
    def __init__(self, label=None, callback=None):
        self.label = label
        self.callback = callback


class Window:
    def __init__(self, parent: tk.Toplevel, window_title=None, additional_menus=None):
        # The master tk object
        self.parent = parent
        self.master = tk.Toplevel(parent)
        # self.master = parent
        self.menubar = tk.Menu(self.master)

        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="New")
        filemenu.add_command(label="Close")
        self.menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Edit")
        editmenu.add_command(label="Change something")
        self.menubar.add_cascade(label="Edit", menu=editmenu)

        if additional_menus != None:
            for cascade in additional_menus:
                cascade_menu = tk.Menu(self.menubar, tearoff=0)
                commands = additional_menus[cascade]
                for item in commands:
                    cascade_menu.add_command(label=item.label, command=item.callback)
                self.menubar.add_cascade(label=cascade, menu=cascade_menu)

        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="Help me!")
        helpmenu.add_command(label="About")
        self.menubar.add_cascade(label="Help", menu=helpmenu)

        # Setup the plot area, stored lines, and setup the menu now that all variables exist.
        self.master.config(menu=self.menubar)

def sayHello():
    print("Hello, world!")

def sayGoodbye():
    print("Goodbye, world!")

def greet():
    print("What's up?")

def snooze():
    print("Snoozing for 15 minutes")

def alarm():
    print("annoying sounds!")

def sleep():
    print("Time for bed!")

if __name__=="__main__":
    root = tk.Tk()

    talkingMenu = [MenuItems("Hello", sayHello), MenuItems("Goodbye", sayGoodbye), MenuItems("Greeting", greet)]
    clockMenu = [MenuItems("Snooze", snooze), MenuItems("Alarm", alarm), MenuItems("Sleep", sleep)]
    newmenus = {"Chatterbox": talkingMenu, "Clock": clockMenu}

    app = Window(root, additional_menus=newmenus)

    root.mainloop()