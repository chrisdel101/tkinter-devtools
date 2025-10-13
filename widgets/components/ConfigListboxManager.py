import tkinter as tk

"""

Inside Left window of the devtools with config settings.
Allows editing of the selected item in the listbox.
https://stackoverflow.com/a/64611569/5972531

"""
class ConfigListboxManager(tk.Listbox):

    def __init__(self, master, width, set_node_selected_callback): 
        self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        tk.Listbox.__init__(self, master=master, width=width,  yscrollcommand = self.scroll_bar.set, bg="red")
        self.editting_item_indext:int | None = None
        self._set_node_selected_callback = set_node_selected_callback
        # listener - for editing an entry using dbl click - not used in creating init val
        self.bind("<Double-1>", self.start_update)
        self.scroll_bar.pack( side = tk.RIGHT, fill = tk.Y)

    def start_update(self, event):
        # index of clicked item on list
        updating_item_index: int = self.index(f"@{event.x},{event.y}")
        self.handle_entry_input(index=updating_item_index, set_node_selected_callback=self._set_node_selected_callback)
        return "break"

    def handle_entry_input(self, index, set_node_selected_callback):
        self.editting_item_index = index
        text = self.get(index)
        # coords of y1 inside bb rect
        y0 = self.bbox(index)[1]
        # add an entry box on top of listbox item
        entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
        # listener - fire callback to handle entry value
        entry.bind("<Return>", lambda e: self.accept_edit(e, index, set_node_selected_callback))
        # listener - fire callback to cancel and exit entry 
        entry.bind("<Escape>", self.cancel_update)
        # TODO add focus off reject edit
        # add the text from the item into the entry
        entry.insert(0, text)
        # set the points to hightlight the entry text
        entry.selection_from(0)
        entry.selection_to("end")
        entry.place(relx=0, y=y0, relwidth=1, width=-1)
        # not hightlight the entry text
        entry.focus_set()
        # sets to grab all inputs - does not allow other inputs while this is active
        entry.grab_set()
    @staticmethod
    def cancel_update(event):
        event.widget.destroy()
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    def accept_edit(self, event, index, set_node_selected_callback):
        new_data = event.widget.get()
        # delete empty entry
        if not new_data:
            print("No data entered, cancelling edit.")
            self.delete(index)
            self.cancel_update(event)
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
        self.delete(self.editting_item_index)
        self.insert(self.editting_item_index, new_data) 
        # send callback to update widget inside treeview
        # - options: set_tree_item_from_entry_value
        set_node_selected_callback(event, changes_dict)
        event.widget.destroy()
        return changes_dict

    
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

        