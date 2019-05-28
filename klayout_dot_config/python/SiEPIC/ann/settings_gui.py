import tkinter as tk
from tkinter import ttk
# from SiEPIC.ann.models.components import Component

class SettingsGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.title("Monte Carlo Simulation")

        padx = 5
        pady = 5

        bbox = tk.Frame(padx=padx, pady=pady)
        bbox.pack()

        notebook = ttk.Notebook(bbox)
        notebook.pack(fill=tk.BOTH)
        
        models = tk.Frame(notebook, padx=padx, pady=pady)
        tk.Label(models, text="Component").grid(row=0, column=0)
        tk.Entry(models).grid(row=0, column=1)
        notebook.add(models, text="Models")

        self.after(0, self.deiconify)

    def on_closing(self):
        self.withdraw()
        self.quit()
        self.destroy()

if __name__ == "__main__":
    gui = SettingsGUI()
    gui.mainloop()