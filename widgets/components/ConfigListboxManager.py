import logging
import tkinter as tk

from constants import MAX_KEY_WIDTH
from style import Style
from utils import Utils

"""

Inside Left window of the devtools with config settings.
Allows editing of the selected item in the listbox.
https://stackoverflow.com/a/64611569/5972531

"""
class ConfigListboxManager(tk.Listbox):

    def __init__(self, master, update_current_selected_item_node_callback, **styles): 
        self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        tk.Listbox.__init__(self, master=master, width=styles.get('width'),  yscrollcommand = self.scroll_bar.set, bg=styles.get('bg'), font=styles.get('font'))
        self.editting_item_indext:int | None = None
        self._update_current_selected_item_node_callback = update_current_selected_item_node_callback
        # listener on listbox - for editing an entry using dbl click - not used in creating init val
        self.bind("<Double-1>", self.start_update)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        # store key val dict 
        self.items_store_dict: dict = {}

    def _get_index_from_event_coords(self, event):
        selected_index: int = self.index(f"@{event.x},{event.y}")
        return selected_index

    def set_items_store_dict(self, index, item_dict):
        self.items_store_dict[index] = item_dict

    def start_update(self, event):
        # index of clicked item on list
        updating_item_index: int = self._get_index_from_event_coords(event)
        
        self.handle_create_entry_input(index=updating_item_index, update_current_selected_item_node_callback=self._update_current_selected_item_node_callback)
    # when items clicked add entry items to the line
    # - add listeners to entrys
    def handle_create_entry_input(self, index, update_current_selected_item_node_callback):
        self.editting_item_index = index
        full_txt_str = self.get(index)
        changes_dict  = Utils.build_split_str_pairs_dict(full_txt_str, ":")
        # coords of y1 inside bb rect
        y0 = self.bbox(index)[1]
        # add an entry box on top of listbox item
        key_entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
       
        # TODO add focus off reject edit
        # add the text from the item into the key_entry
        key_entry.insert(0, changes_dict.get('key'))
        # set the points to hightlight the key_entry text
        key_entry.selection_from(0)
        key_entry.selection_to("end")
        key_entry.place(relx=0, y=y0, relwidth=1, width=-1)
    
        # --- VALUE ENTRY ---
        value_entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
         # listener - fire callback to handle key_entry value
       
        value_entry.insert(0, changes_dict.get('value'))
        value_entry.selection_from(0)
        value_entry.selection_to("end")
        value_entry.place(relx=0.3, y=y0, relwidth=0.58, width=-1)
        # not hightlight the key_entry text
        value_entry.focus_set()
        # sets to grab all inputs - does not allow other inputs while this is active
        value_entry.grab_set()
        # store changes dict at index
        self.set_items_store_dict(index, changes_dict)
         # listener - fire callback to handle key_entry value
        key_entry.bind("<Return>", lambda e: self.accept_edit(e, index, update_current_selected_item_node_callback))
        # listener - fire callback to cancel and exit key_entry 
        key_entry.bind("<Escape>", lambda e: self.cancel_update(e, value_entry))
        value_entry.bind("<Return>", lambda e: self.accept_edit(e, index, update_current_selected_item_node_callback))
        # listener - fire callback to cancel and exit value_entry
        value_entry.bind("<Escape>", lambda e: self.cancel_update(e, key_entry))

    @staticmethod
    def cancel_update(event, *args):
        event.widget.destroy()
        for arg in args:
            arg.destroy()
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    def accept_edit(self, event, index, update_current_selected_item_node_callback):
        current_index = self._get_index_from_event_coords(event)
        # get full dict of values
        stored_changes_dict = self.items_store_dict.get(current_index)
        # get entry value that's changed
        input_data = event.widget.get()
        # delete empty entry
        if not input_data:
            print("No data entered, cancelling edit.")
            self.delete(index)
            self.cancel_update(event)
            return
        if stored_changes_dict.get('value') == input_data:
            print("No changes made, cancelling edit.")
            self.cancel_update(event)
            return
        # delete data at current index and insert new data there
        self.delete(self.editting_item_index)
        self.insert(self.editting_item_index, Utils.build_full_input_str(stored_changes_dict.get('key'), input_data))
        # send callback to update widget inside treeview
        # - options: set_tree_item_from_entry_value
        update_current_selected_item_node_callback(event, stored_changes_dict)
        # update the stored val dict w changed val
        self.set_items_store_dict(current_index, {
            'key': stored_changes_dict.get('key'),
            'value': input_data
        })
        event.widget.destroy()
        return input_data

    def delete_contents(self):
        self.delete(0, tk.END)

    def insert_all(self, config_dict):
         for key in config_dict:
            # insert selected node into styles_window_listbox window
            display = f"{key}: {config_dict[key]}"
            # this auto sizes w/o adding styles
            self.insert(tk.END, display)

    def insert_item(self, index=tk.END, value=None):
        if value is None:
            logging.info("listbox value is None.")
        self.insert(index, value)

        