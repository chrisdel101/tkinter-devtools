import tkinter as tk

class ConfigListboxManager(tk.Listbox):
    """

    Inside Left window of the devtools with config settings.
    Allows editing of the selected item in the listbox.
    https://stackoverflow.com/a/64611569/5972531

    """

    def __init__(self, master, width, set_tree_item_callback=None): 
        self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        tk.Listbox.__init__(self, master=master, width=width,  yscrollcommand = self.scroll_bar.set, bg="red")
        self.edit_item = None
        # listener - for editing an entry using dbl click - not used in creating init val
        self.bind("<Double-1>", lambda e: self.start_edit(e, set_tree_item_callback))
        self.scroll_bar.pack( side = tk.RIGHT, fill = tk.Y)

    def start_edit(self, event, callback):
        index = self.index(f"@{event.x},{event.y}")
        self.handle_entry(index, callback)
        return "break"

    def handle_entry(self, index, callback):
        self.edit_item = index
        text = self.get(index)
        # coords of y1 inside bb rect
        y0 = self.bbox(index)[1]
        entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
        # listener - fire callback to handle entry value
        entry.bind("<Return>", lambda e: self.accept_edit(e, index, callback))
        # listener - fire callback to cancel and exit entry 
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
    # handle entry within an entry inside listbox
    def accept_edit(self, event, index, callback):
        new_data = event.widget.get()
        # delete empty entry
        if not new_data:
            print("No data entered, cancelling edit.")
            self.delete(index)
            self.cancel_edit(event)
            return
        # get the value of the selected items - it's string currently
        split_list_items: list = new_data.split(":")
        key = split_list_items[0]
        value = split_list_items[1]
        changes_dict  = {
            'key': key,
            'value': value.strip(),
        }
        # delete data at current index and insert new data there
        self.delete(self.edit_item)
        self.insert(self.edit_item, new_data) 
        # send callback to update widget inside treeview  
        callback(event,changes_dict)
        event.widget.destroy()

    
    def delete_contents(self):
        self.delete(0, tk.END)

    def insert_all(self, config_dict):
         for key in config_dict:
            # insert selected node into styles_window_listbox window
            self.insert(tk.END, f"{key}: {config_dict[key]}\n")

    def insert_item(self, index=tk.END, value=None):
        if value is None:
            print("listbox value is None.")
        self.insert(index, value)

        