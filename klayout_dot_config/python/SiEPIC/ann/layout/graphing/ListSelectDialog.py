import tkinter as tk
from tkinter import simpledialog

class ListSelectDeleteDialog:
    """Opens a dialog window presenting a list of items passed in as a parameter.

    Delete button removes items from the list. Deleted items are the return value.

    Usage: ListSelectDeleteDialog(master: tk.Toplevel).askdeletelist(startlist: list)
    """

    def __init__(self, master: tk.Toplevel):
        self.master = master

    def askdeletelist(self, startlist: list):
        self.listbox = tk.Listbox(self.master)
        self.listbox.pack()
        self.deleted = []
        self.leftover = startlist
        self.success = True
        self.master.protocol("WM_DELETE_WINDOW", self._cancel)

        for item in startlist:
            self.listbox.insert(tk.END, item)

        frame_okCancel = tk.Frame(self.master)
        deleteBtn = tk.Button(frame_okCancel, text="Delete", command=lambda: self._delete(self.listbox))
        deleteBtn.grid(column=0, row=0)
        okBtn = tk.Button(frame_okCancel, text="Ok", command=self._on_close)
        okBtn.grid(column=1, row=0)
        cancelBtn = tk.Button(frame_okCancel, text="Cancel", command=self._cancel)
        cancelBtn.grid(column=2, row=0)
        frame_okCancel.pack()

        self.master.grab_set()
        self.master.wait_window(self.master)
        if self.success:
            return self.deleted
        else:
            return None

    def _delete(self, listbox: tk.Listbox):
        selection = listbox.curselection()[0]
        self.deleted.append(self.leftover.pop(selection))
        listbox.delete(selection)        

    def _cancel(self):
        self.success = False
        self._on_close()

    def _on_close(self):
        self.master.destroy()


class ListSelectRenameDialog:
    """Opens a dialog window presenting a list of items passed in as a parameter.

    Rename button opens a text dialog to rename an item from the list. Returns a tuple, the original name
    and the new name.

    Usage: ListSelectRenameDialog(master: tk.Toplevel).askrenamelist(startlist: list)
    """

    def __init__(self, master: tk.Toplevel):
        self.master = master

    def askrenamelist(self, startlist: list):
        self.listbox = tk.Listbox(self.master)
        self.listbox.pack()
        self.leftover = startlist
        self.success = True
        self.master.protocol("WM_DELETE_WINDOW", self._cancel)

        for item in startlist:
            self.listbox.insert(tk.END, item)

        frame_okCancel = tk.Frame(self.master)
        deleteBtn = tk.Button(frame_okCancel, text="Rename", command=lambda: self._rename(self.listbox))
        deleteBtn.grid(column=0, row=0)
        cancelBtn = tk.Button(frame_okCancel, text="Cancel", command=self._cancel)
        cancelBtn.grid(column=1, row=0)
        frame_okCancel.pack()

        self.master.grab_set()
        self.master.wait_window(self.master)
        if self.success:
            return self.original, self.final
        else:
            return None, None

    def _rename(self, listbox: tk.Listbox):
        selection = listbox.curselection()[0]
        self.original = self.leftover.pop(selection)
        self.master.withdraw()
        self.final = simpledialog.askstring("Rename", "Enter new name for line: " + self.original)
        self.master.destroy()

    def _cancel(self):
        self.success = False
        self._on_close()

    def _on_close(self):
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    orig, final = ListSelectRenameDialog(tk.Toplevel(root)).askrenamelist(["first","second","third"])
    print(orig, final)