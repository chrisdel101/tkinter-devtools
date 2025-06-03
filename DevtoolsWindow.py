import tkinter as tk
from tkinter import ttk
from TreeView import TreeView
from ConfigListbox import ConfigListbox

class DevtoolsWindow:
    def __init__(self, root, title="Devtools"):
        # Toplevel is wrapper for two inner windows - does not pack
        self.top_level = tk.Toplevel(root, background='red')
        self.top_level.title(title)
        self.root = root
        # right window - tree struct inside tool
                
        # style = ttk.Style()
        # style.configure("Custom.Treeview", borderwidth=0, padding=0)
        # style.layout("Custom.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        self.styles_window_listbox = ConfigListbox(self.top_level, width=50, callback=self.get_editted_value)
        self.tree = TreeView(self.top_level, self.styles_window_listbox)
        self.tree.bind_tree_select()
        self.tree.build_tree(root)
        # Select the first item by default
        self.tree.select_tree_item(self.tree.get_children()[0])  
        self.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        
        self.styles_window_listbox.pack(side="left", fill="both", expand=True)

        self.store_tree_widgets_by_id = {}
        
    def get_editted_value(self, e, changes_dict):
        self.tree.update_tree_item(changes_dict)   
    
    

