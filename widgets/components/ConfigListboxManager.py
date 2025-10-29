import logging
import tkinter as tk
from tkinter import ttk

from constants import ComboBoxState
from maps import OPTIONS
from utils import Utils

"""

Inside Left window of the devtools with config settings.
Allows editing of the selected item in the listbox.
https://stackoverflow.com/a/64611569/5972531

"""
class ConfigListboxManager(tk.Listbox):

    def __init__(self, master, update_current_selected_item_node_callback, **styles): 
        self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        tk.Listbox.__init__(self, master=master, width=styles.get('width'),  yscrollcommand = self.scroll_bar.set, font=styles.get('font'))
        self.styles = styles
        self.editting_item_index:int | None = None
        self._update_current_selected_item_node_callback = update_current_selected_item_node_callback
        # listener on listbox - for editing an entry using dbl click - not used in creating init val
        self.bind("<Double-1>", self.start_update)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
       
    # use event x and y w tk index - get listbox item index
    def _get_index_from_event_coords(self, event):
        selected_index: int = self.index(f"@{event.x},{event.y}")
        return selected_index

    def set_items_store_dict(self, index, item_dict):
        self.items_store_dict[index] = item_dict

    def start_update(self, event):
        # index of clicked item on list
        updating_item_index: int = self._get_index_from_event_coords(event)
        
        self.handle_create_entry_input(
            index=updating_item_index, update_current_selected_item_node_callback=self._update_current_selected_item_node_callback
        )
        return "break"
    # when items clicked add entry items to the line
    # - add listeners to entrys
    def handle_create_entry_input(self, index, update_current_selected_item_node_callback):
        self.editting_item_index = index
        full_txt_str = self.get(index)
        changes_dict  = Utils.build_split_str_pairs_dict(full_txt_str, ":")
        # coords of y1 inside bb rect
        y0 = self.bbox(index)[1]
        # --- KEY ENTRY ---
        # add an entry box on top of listbox item
        key_entry = tk.Entry(self, **self.styles['entry'], **self.styles['key_entry'])
        # add the text from the item into the key_entry - just place it but dont allow focus
        key_entry.insert(0, changes_dict.get('key'))
        key_entry.selection_from(0)
        key_entry.selection_to("end")
        key_entry.place(relx=0, y=y0, relwidth=1, width=-1)
        # get value from dict map
        item_mapped_values: list[str] | str = self._get_config_value_options(key_entry.get())
        # if vals are list use dropdown
        if isinstance(item_mapped_values, list):
            logging.debug(f"Mapped values for key {key_entry.get()}: {item_mapped_values}")
            # --- DROP DOWN ENTRY ---
            combo_box = ttk.Combobox(self, 
                values=item_mapped_values, 
                state=self._get_config_option_state(key_entry.get())
            )
            # set first item to show up
            combo_box.set(changes_dict.get('value'))
            # combo_box.bind('<<ComboboxSelected>>', lambda e: self.accept_edit_to_page_widget(e, index, update_current_selected_item_node_callback, key_entry))
            # if state is not read only allow return event
            combo_box.bind('<Return>', lambda e: None
            if str(combo_box.cget("state")) == ComboBoxState.READONLY.value
            else self.accept_edit_to_page_widget(e, index, update_current_selected_item_node_callback, key_entry))
            # combo_box.bind("<FocusOut>", lambda e: self.cancel_update(e, key_entry))
            # combo_box.bind("<FocusOut>", lambda e: self.on_focus_out(e, key_entry))
            combo_box.bind("<Escape>", lambda e: self.cancel_update(e, key_entry))
            combo_box.place(relx=0.3, y=y0, relwidth=0.58, width=-1)
            combo_box.focus_set()
        # if vals are str use entry

        elif isinstance(item_mapped_values, str) or item_mapped_values is None:
             # --- VALUE ENTRY ---
            value_entry = tk.Entry(self, **self.styles['entry'])
            value_entry.insert(0, changes_dict.get('value'))
            value_entry.selection_from(0)
            value_entry.selection_to("end")
            value_entry.place(relx=0.3, y=y0, relwidth=0.58, width=-1)
            value_entry.focus_set()
            value_entry.bind("<Return>", lambda e: self.accept_edit_to_page_widget(e, index, update_current_selected_item_node_callback, key_entry))
            for ev in ["<Escape>", "<FocusOut>"]:
                value_entry.bind(ev, lambda e: self.cancel_update(e, key_entry))
        
    # get options of config properties to use in dropdown
    @staticmethod
    def _get_config_value_options(key_str_value=None) -> list| str:
        if not key_str_value:
            return 
        options_list = (OPTIONS.get(key_str_value) or {}).get('values')
        if options_list is None:
            logging.error(f"No options found for key: {key_str_value}")
        return options_list
    # get get state from mapped config vals - for set vals make readonly else normal
    @staticmethod
    def _get_config_option_state(key_str_value=None) -> list| str:
        if not key_str_value:
            return
        state = (OPTIONS.get(key_str_value) or {}).get('state')
        if state is None:
            logging.error(f"No state found for key: {key_str_value}")
        return state

    @staticmethod
    def cancel_update(event, *args):
        event.widget.destroy()
        for arg in args:
            arg.destroy()
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    def accept_edit_to_page_widget(self, event, index, update_current_selected_item_node_callback, key_entry):

        # value from the entries
        input_data = event.widget.get()
        key_entry_value = key_entry.get()
        # delete empty entry
        if not input_data:
            print("No data entered, cancelling edit.")
            self.delete(index)
            self.cancel_update(event)
            return

        # delete data at current index and insert new data there
        self.delete(self.editting_item_index)
        self.insert(self.editting_item_index, Utils.build_full_input_str(key_entry_value, input_data))
        # send callback to update widget inside treeview
        # - options: set_tree_item_from_entry_value
        update_current_selected_item_node_callback(event, {
            'key': key_entry_value,
            'value': input_data
        })
    
        self.cancel_update(event, key_entry)
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

    def _on_combobox_focus_out(self, event, key_entry): 
        combo = event.widget
        # If the user actually made a selection, ignore this FocusOut
        if getattr(combo, "_was_selected", False):
            combo._was_selected = False  # reset flag
            return
        # Otherwise, they really left the field — cancel
        self.cancel_update(event, key_entry)

    def on_focus_out(self, event, key_entry):
        combo = event.widget
        self._handle_real_focus_out(combo, event, key_entry)

    def _handle_real_focus_out(self, combo, event, key_entry):
        try:
            focused = combo.focus_get()
        except Exception:
            focused = None
        # Only cancel if the combobox (and its dropdown) truly lost focus
        print(f"Focused widget: {focused}, Combo widget: {combo}")
        if not str(focused).startswith(str(combo)):
            pass
            # self.cancel_update(event, key_entry)
