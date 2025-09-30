from ConfigListboxManager import ConfigListboxManager
from windows.WindowFrame import WindowFrame
import tkinter as tk
from tkinter import ttk

class RightWindowFrame(WindowFrame):
    def __init__(self, master=None, set_tree_item_callback=None, get_tree_item_callback=None):
        super().__init__(master)
        # button header
        self.header_frame = tk.Frame(self, height=30, bg="lightgrey")
        # sets value on 
        self._set_tree_item_callback = set_tree_item_callback
        self._get_tree_item_callback = get_tree_item_callback
        # callback - send changes in right window to left window treeview
        self.styles_window_listbox = ConfigListboxManager(self, width=50, set_tree_item_callback=set_tree_item_callback)
        
        self.add_config_button = tk.Button(self.header_frame, text="+", command=self.handle_add)
        self.subtract_config_button = tk.Button(self.header_frame, text="-", command=self.handle_subract)
        # pack add button
        self.add_config_button.pack(side="left", padx=5, pady=5)
        # pack subtract button
        self.subtract_config_button.pack(side="left", padx=5, pady=5)
         # pack header
        self.header_frame.pack(side="top", fill="x", expand=False, padx=0, pady=0, ipady=0, ipadx=0)
         # pack listbox
        self.styles_window_listbox.pack(side="left", fill="both", expand=True)

    
    def handle_add(self):
        current_listbox_selection = self.styles_window_listbox.curselection()
        current_treeview_item = self._get_tree_item_callback()
        # cb = ttk.Combobox(self, values=a)
        # if none selected insert at top
        if len(current_listbox_selection) == 0:
            self.styles_window_listbox.insert(0, "")
            self.styles_window_listbox.handle_entry(0, self._set_tree_item_callback)
        # insert after selected_item
        else:
            #  get selected tuple 
            current_selection_index = current_listbox_selection[0]
            self.styles_window_listbox.insert(current_selection_index+1, "")
            self.styles_window_listbox.handle_entry(current_selection_index+1, self._set_tree_item_callback)

    def handle_subract(self):
        current_selection = self.styles_window_listbox.curselection()
        
        if len(current_selection) == 0:
            print("No item selected to remove.")
            return
        else:
            current_selection_index = current_selection[0]
            self.styles_window_listbox.delete(current_selection_index)