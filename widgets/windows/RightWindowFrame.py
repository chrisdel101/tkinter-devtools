from constants import ListBoxEntryInputAction
from widgets.components.ConfigListboxManager import ConfigListboxManager
import tkinter as tk

class RightWindowFrame(tk.Frame):
    def __init__(self, master, get_tree_item_callback, set_tree_item_callback):
        super().__init__(master, width=300, height=500, bg="red")
        # button header
        self.header_frame = tk.Frame(self, height=50, bg="lightgrey")
        # sets value on 
        self._set_tree_item_callback = set_tree_item_callback
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
        # self.header_frame.bind("<Button-1>", self._config_listbox_mngr.cancel_update)
         # pack listbox
        # config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
        # self.pack(fill="both", expand=True)

    def set_listbox_manager(self, config_listbox_mngr):
        setattr(self, '_config_listbox_mngr', config_listbox_mngr)
        self._config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
    def handle_add(self):
        current_listbox_selection = self._config_listbox_mngr.curselection()
        current_treeview_item = self._get_tree_item_callback()
        # cb = ttk.Combobox(self, values=a)
        if len(current_listbox_selection) == 0:
            # if none selected insert at top
            insert_at_index = 0
        else:
            # insert after selected_item
            current_selection_index = current_listbox_selection[0]
            insert_at_index = current_selection_index + 1
       
        self._config_listbox_mngr.insert(insert_at_index, "")
        self._config_listbox_mngr.handle_entry_input_create(
            index=insert_at_index,
            update_current_selected_item_node_callback=self._set_tree_item_callback
        )
        

    def handle_subract(self):
        current_selection = self._config_listbox_mngr.curselection()
        
        if len(current_selection) == 0:
            print("No item selected to remove.")
            return
        else:
            current_selection_index = current_selection[0]
            self._config_listbox_mngr.delete(current_selection_index)