import logging
import tkinter as tk
from tkinter import Spinbox

from constants import ComboBoxState, OptionBoxState
from maps import OPTIONS
from utils import Utils

"""

Inside Left window of the devtools with config settings.
Allows editing of the selected item in the listbox.
https://stackoverflow.com/a/64611569/5972531

"""
class ConfigListboxManager(tk.Listbox):

    def __init__(self, master, update_current_selected_item_node_callback, toggle_option_box_state_callback, **styles): 
        self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        tk.Listbox.__init__(self, master=master, width=styles.get('width'),  yscrollcommand = self.scroll_bar.set, font=styles.get('font'))
        self.styles = styles
        self.editting_item_index:int | None = None
        self._update_current_selected_item_node_callback = update_current_selected_item_node_callback
        # listener on listbox - for editing an entry using dbl click - not used in creating init val
        self._toggle_option_box_state_callback = toggle_option_box_state_callback
        self.bind("<Double-1>", self.start_update)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.option_box_state = OptionBoxState.CLOSED.value
       
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
        item_mapped_values: list[str] | None = self._get_config_value_options(key_entry.get())
        # if vals are list use dropdown
        if isinstance(item_mapped_values, list):
            # logging.debug(f"Mapped values for key {key_entry.get()}: {item_mapped_values}")
            # --- DROP DOWN ENTRY ---
            value_inside = tk.StringVar(self)
            value_inside.set(item_mapped_values[0])
            # like bind - get selected value from drop down
            option_box = tk.OptionMenu(self,
                value_inside,
                *item_mapped_values,
               )
            value_inside.trace_add('write', lambda *args:self.accept_edit_to_page_widget(option_box, index, value_entry_widget=value_inside, key_entry_widget=key_entry, update_current_selected_item_node_callback=update_current_selected_item_node_callback))
                        # if state is not read only allow return event
            option_box.bind('<Return>', lambda e: self.accept_edit_to_page_widget(widget=e.widget, index=index, value_entry_widget=e.widget, key_entry_widget=key_entry, update_current_selected_item_node_callback=update_current_selected_item_node_callback))
            option_box.bind("<Escape>", lambda e: self.cancel_update(option_box, key_entry))
            option_box.place(relx=0.3, y=y0, relwidth=0.58, width=-1)
            option_box.focus_set()
            # get menu btn parent - only way to detect bind 
            btn = option_box.children['menu'].master
            # btn.bind("<ButtonPress-1>", self._toggle_option_box_state_callback)
            btn.bind("<FocusOut>", lambda e: self.cancel_update(option_box, key_entry))
            # btn.bind("<FocusOut>",  self.set_box_state_on_open)
        # if vals are str use entry
        elif isinstance(item_mapped_values, str) or item_mapped_values is None:
             # --- VALUE ENTRY ---
            value_entry = tk.Entry(self, **self.styles['entry'])
            value_entry.insert(0, changes_dict.get('value'))
            value_entry.selection_from(0)
            value_entry.selection_to("end")
            value_entry.place(relx=0.3, y=y0, relwidth=0.58, width=-1)
            value_entry.focus_set()
            value_entry.bind("<Return>", lambda e: self.accept_edit_to_page_widget(widget=e.widget, index=index, value_entry_widget=e.widget, key_entry_widget=key_entry, update_current_selected_item_node_callback=update_current_selected_item_node_callback))
            for ev in ["<Escape>", "<FocusOut>"]:
                value_entry.bind(ev, lambda e: self.cancel_update(e.widget, key_entry))
        
    # get options of config properties to use in dropdown - if they exist
    @staticmethod
    def _get_config_value_options(key_str_value=None) -> list| str:
        if not key_str_value:
            return 
        # check for options in map
        options_list = (OPTIONS.get(key_str_value) or {}).get('values')
        if options_list is None:
            logging.debug(f"{key_str_value} not mapped. Using Entry.")
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
    def cancel_update(widget, *args):
        widget.destroy()
        for arg in args:
            arg.destroy()
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    def accept_edit_to_page_widget(self, 
            widget: tk.Widget, index: int, value_entry_widget: str, key_entry_widget: str, update_current_selected_item_node_callback: callable):
        
        # delete empty entry
        is_val_widget = isinstance(value_entry_widget, tk.Widget) or isinstance(value_entry_widget, tk.StringVar)
        is_key_widget = isinstance(key_entry_widget, tk.Widget)
        if not is_val_widget or not is_key_widget:
            fn = lambda val_type: logging.error(f"No data received for {val_type}. Cancelling edit.")
            fn("value_entry_widget") if not is_val_widget else fn("key_entry_widget")


            self.delete(index)
            self.cancel_update(value_entry_widget, key_entry_widget)
            return

        # delete data at current index and insert new data there
        self.delete(self.editting_item_index)
        self.insert(self.editting_item_index, Utils.build_full_input_str(key_entry_widget.get(), value_entry_widget.get()))
        # send callback to update widget inside treeview
        # - options: set_tree_item_from_entry_value
        k = key_entry_widget.get()
        v = value_entry_widget.get()
        update_current_selected_item_node_callback({
            'key': k,
            'value': v
        })
    
        self.cancel_update(widget, key_entry_widget)
        return v

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

    # set to open on click - only handles open since close is not detectable
    def set_box_state_on_open(self, event):
        # logging.debug(f"state: {self.option_box_state}")
        # if open set to closed - else set to open
        if self.option_box_state == OptionBoxState.CLOSED.value:
            self.option_box_state = OptionBoxState.OPEN.value
            # logging.debug("Option box opened.")
        else:
            self.option_box_state = OptionBoxState.CLOSED.value
            # logging.debug("Option box closed.")