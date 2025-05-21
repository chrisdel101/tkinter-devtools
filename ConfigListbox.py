import tkinter as tk

class ConfigListbox(tk.Listbox):
    """
    Left window of the devtools with config settings.
    Allows editing of the selected item in the listbox.
    https://stackoverflow.com/a/64611569/5972531

    """

    def __init__(self, master, width): 
        tk.Listbox.__init__(self, master=master, width=width)
        self.edit_item = None
        self.bind("<Double-1>", self._start_edit)
    
    
    def _start_edit(self, event):
        index = self.index(f"@{event.x},{event.y}")
        self.start_edit(index)
        return "break"

    def start_edit(self, index):
        self.edit_item = index
        text = self.get(index)
        y0 = self.bbox(index)[1]
        entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
        entry.bind("<Return>", self.accept_edit)
        entry.bind("<Escape>", self.cancel_edit)

        # TODO add focus off reject edit

        entry.insert(0, text)
        entry.selection_from(0)
        entry.selection_to("end")
        entry.place(relx=0, y=y0, relwidth=1, width=-1)
        entry.focus_set()
        entry.grab_set()

    def cancel_edit(self, event):
        event.widget.destroy()

    def accept_edit(self, event):
        new_data = event.widget.get()
        self.delete(self.edit_item)
        self.insert(self.edit_item, new_data)
        event.widget.destroy()

    def delete_contents(self):
        self.delete(0, tk.END)

    def insert_all(self, config_dict):
         for key in config_dict:
            # insert selected node into styles_window_listbox window
            self.insert(tk.END, f"{key}: {config_dict[key][-1]}\n")

    def insert_item(self, index=tk.END, value=None):
        if value is None:
            print("listbox value is None.")
        self.insert(index, value)

        