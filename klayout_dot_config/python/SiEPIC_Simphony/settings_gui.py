import tkinter as tk
from tkinter import ttk

from SiEPIC_Simphony import config

class SelectModelDialog:
    def __init__(self, master: tk.Toplevel):
        self.master = master
        self.success = False
        self.master.title('Select New Model')

    def present_list(self, model_list):
        self.listbox = tk.Listbox(self.master, width=50)
        self.listbox.pack()

        for item in model_list:
            self.listbox.insert(tk.END, item)

        self.listbox.bind("<Double-1>", self.on_select)

        self.master.wait_window(self.master)
        if self.success:
            return self.selection
        else:
            return None

    def on_select(self, event):
        self.selection = self.listbox.get(self.listbox.curselection())
        self.success = True
        self.master.destroy()
        

class SettingsGui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        master = self
        self.title('Settings')

        list_frame = tk.Frame(master)
        list_frame.grid(column=0, row=0, sticky='nsew')
        master.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(list_frame, selectmode='browse')
        tree = self.tree
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.pack(side='left', expand=True, fill='y')

        tree.configure(yscrollcommand=vsb.set)
        tree.bind("<Double-1>", self.on_click)

        tree["columns"]=("one")
        tree.column("#0", width=270, minwidth=270, stretch=tk.NO)
        tree.column("one", width=500, minwidth=200)

        tree.heading("#0",text="Component",anchor=tk.W)
        tree.heading("one", text="Simulation Model",anchor=tk.W)

        for key, value in config.selected_models.items():
            tree.insert("", 'end', key, text=key, values=(value, ))

    def on_click(self, event):
        item = self.tree.focus()
        key = self.tree.item(item, 'text')
        selection = SelectModelDialog(tk.Toplevel(self)).present_list(sorted(list(config.all_models.keys())))
        if selection:
            config.set_model(key, selection)
            self.tree.item(key, values=(config.selected_models[key],))

def settings_gui():
    app = SettingsGui()
    app.mainloop()