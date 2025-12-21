from __future__ import annotations
import tkinter as tk
from typing import Any
from devtools.style import Style
from devtools.components.widgets.TreeView import TreeView

class LeftWindowFrame(tk.Frame):
    def __init__(self, root, master, observable, store, listbox_widget, set_current_node_selected_callback):
        super().__init__(master,  **Style.left_window_frame)
        self._observable = observable
        self._store = store
        self._observable.register_observer(self)

       # pass the other window listbox down for updating it from left window
        self.tree = TreeView(
            root=root, 
            master=self, 
            observable=self._observable,
            store=self._store,
            listbox_widget=listbox_widget
        )
        self.tree.bind_tree_select(set_current_node_selected_callback=set_current_node_selected_callback)
        self.tree.build_tree(root)

        self.tree.select_tree_item(self.tree.get_children()[0]) 
        # pack treeview 
        self.tree.pack(side="left", fill="both", expand=True)
        self.selected_item = None
        
    def notify(self, **kwargs: dict[str, Any]):
            pass
    
