from widgets.components.ConfigListboxManager import ConfigListboxManager
from widgets.windows.WindowFrame import WindowFrame
import tkinter as tk
from tkinter import ttk

class RightWindowFrame(tk.Frame):
    def __init__(self, master, get_tree_item_callback, set_tree_item_callback):
        super().__init__(master, width=300, height=500, bg="red")
        # button header
        self.header_frame = tk.Frame(self, height=50, bg="lightgrey")
        # self.header_frame.bind("<Button-1>", lambda e: print("Click"))
        # self.header_frame.bind("<Button-1>", lambda e: print("Click"))
        # sets value on 
        self._set_tree_item_callback = set_tree_item_callback
        self._get_tree_item_callback = get_tree_item_callback
        # callback - send changes in right window to left window treeview
        self._config_listbox_mngr: ConfigListboxManager = None
        
        # self.add_config_button = tk.Button(self.header_frame, text="+", command=self.handle_add)
        # self.add_config_button = tk.Button(self.header_frame, text="+", command=self.handle_add)
        # self.subtract_config_button = tk.Button(self.header_frame, text="-", command=self.handle_subract)
        # self.subtract_config_button = tk.Button(self.header_frame, text="-", command=self.handle_subract)
        # # pack add button
        # self.add_config_button.pack(side="left", padx=5, pady=5)
        # # pack subtract button
        # self.subtract_config_button.pack(side="left", padx=5, pady=5)
         # pack header
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
        # if none selected insert at top
        if len(current_listbox_selection) == 0:
            self._config_listbox_mngr.insert(0, "")
            self._config_listbox_mngr.handle_create_entry_input(0, self._set_tree_item_callback)
        # insert after selected_item
        else:
            #  get selected tuple 
            current_selection_index = current_listbox_selection[0]
            self._config_listbox_mngr.insert(current_selection_index + 1, "")
            self._config_listbox_mngr.handle_create_entry_input(current_selection_index + 1, self._set_tree_item_callback)

    def handle_subract(self):
        current_selection = self._config_listbox_mngr.curselection()
        
        if len(current_selection) == 0:
            print("No item selected to remove.")
            return
        else:
            current_selection_index = current_selection[0]
            self._config_listbox_mngr.delete(current_selection_index)