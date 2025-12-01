from __future__ import annotations
from devtools.utils import Utils
from devtools.widgets.components.ConfigListboxManager import ConfigListboxManager
import tkinter as tk

class RightWindowFrame(tk.Frame):
    def __init__(self, master, get_tree_item_callback, update_current_selected_item_node_callback):
        super().__init__(master, width=300, height=500, bg="red")
        # button header
        self.header_frame = tk.Frame(self, height=50, bg="lightgrey")
        # sets value on 
        self._update_current_selected_item_node_callback = update_current_selected_item_node_callback
        self._get_tree_item_callback = get_tree_item_callback
        # callback - send changes in right window to left window treeview
        self._config_listbox_mngr: ConfigListboxManager = None
        
        self.add_config_button = tk.Button(self.header_frame, text="+", command=self.handle_add)
        self.subtract_config_button = tk.Button(self.header_frame, text="-", command=self.handle_subract)
        # pack add button
        self.add_config_button.pack(side="left", padx=5, pady=5)
        # pack subtract button
        self.subtract_config_button.pack(side="left", padx=5, pady=5)
        #  pack header
        self.header_frame.pack(fill="x", expand=True)
        
    # add listbox manager after init - called on the parent window 
    def set_listbox_manager(self, config_listbox_mngr):
        setattr(self, '_config_listbox_mngr', config_listbox_mngr)
        self._config_listbox_mngr.pack(side="bottom", fill="both", expand=True)

    def handle_add(self):
        current_listbox_selection = self._config_listbox_mngr.curselection()
        current_treeview_item = self._get_tree_item_callback()
        if len(current_listbox_selection) == 0:
            # if none selected insert at top
            insert_at_index = 0
        else:
            # insert after selected_item
            current_selection_index = current_listbox_selection[0]
            insert_at_index = current_selection_index + 1
       
        self._config_listbox_mngr.insert(insert_at_index, "")
        # called on the child listbox
        self._config_listbox_mngr.handle_entry_input_create(
            index=insert_at_index,
            update_current_selected_item_node_callback=self._update_current_selected_item_node_callback
        )
        

    def handle_subract(self, _=None):
        # this is tuple format (3,)
        curselection: tuple[int] = self._config_listbox_mngr.curselection()
        current_treeview_item = self._get_tree_item_callback()

        if len(curselection) == 0:
            print("No item selected to remove.")
            return
        else:
            # get value at listbox selected index
            active_item_value =self._config_listbox_mngr.get(tk.ACTIVE)
            if active_item_value:
                changes_dict = Utils.build_split_str_pairs_dict(self._config_listbox_mngr.get(tk.ACTIVE))
                # send update to page widget to set config to zero
                self._update_current_selected_item_node_callback({
                    "key": changes_dict['key'],
                    "value": 0
                })
            # unpack first item from tuple
            current_selection_index, = curselection
            # remove from listbox
            self._config_listbox_mngr.delete(current_selection_index)