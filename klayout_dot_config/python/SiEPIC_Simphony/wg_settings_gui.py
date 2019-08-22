import tkinter as tk
from tkinter import ttk

from SiEPIC_Simphony import config

class SettingsGui(tk.Tk):
    str_default = ''

    def __init__(self):
        tk.Tk.__init__(self)
        master = self
        self.title('Waveguide Settings')

        row = 0
        
        tk.Label(master, text='Model must be "ebeam_wg_integral_1550"\nEnter values (leave blank for default):').grid(column=0, row=row, columnspan=2)
        row += 1

        tk.Label(master, text='Center wavelength [m]:').grid(column=0, row=row)
        self.wl0 = tk.StringVar()
        self.wl0.set(self.translator_in(config.wl0))
        tk.Entry(master, textvariable=self.wl0).grid(column=1, row=row)
        row += 1

        tk.Label(master, text='Effective index (n_eff):').grid(column=0, row=row)
        self.ne = tk.StringVar()
        self.ne.set(self.translator_in(config.ne))
        tk.Entry(master, textvariable=self.ne).grid(column=1, row=row)
        row += 1

        tk.Label(master, text='Group index (n_g):').grid(column=0, row=row)
        self.ng = tk.StringVar()
        self.ng.set(self.translator_in(config.ng))
        tk.Entry(master, textvariable=self.ng).grid(column=1, row=row)
        row += 1

        tk.Label(master, text='Dispersion (n_d):').grid(column=0, row=row)
        self.nd = tk.StringVar()
        self.nd.set(self.translator_in(config.nd))
        tk.Entry(master, textvariable=self.nd).grid(column=1, row=row)
        row += 1

        tk.Button(master, text='Revert to Defaults', command=self.on_revert_defaults).grid(column=0, row=row)
        tk.Button(master, text='OK', command=self.on_ok).grid(column=1, row=row)
        self.bind('<KP_Enter>', self.on_ok)

    def translator_in(self, value):
        if value is not None:
            return str(value)
        else:
            return self.str_default

    def translator_out(self, value):
        if value == self.str_default:
            return None
        else:
            return float(value)

    def on_revert_defaults(self):
        self.wl0.set(self.str_default)
        self.ne.set(self.str_default)
        self.ng.set(self.str_default)
        self.nd.set(self.str_default)

    def on_ok(self, event=None):
        config.wl0 = self.translator_out(self.wl0.get())
        config.ne = self.translator_out(self.ne.get())
        config.ng = self.translator_out(self.ng.get())
        config.nd = self.translator_out(self.nd.get())
        self.withdraw()
        self.quit()
        self.destroy()

def wg_settings_gui():
    app = SettingsGui()
    app.mainloop()

if __name__ == "__main__":
    wg_settings_gui()