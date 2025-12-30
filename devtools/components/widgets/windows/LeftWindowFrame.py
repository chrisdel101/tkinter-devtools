from __future__ import annotations
import tkinter as tk
from typing import Any
from devtools.style import Style
from devtools.components.widgets.TreeView import TreeView

class LeftWindowFrame(tk.Frame):
    def __init__(self, 
            root, 
            master, 
            observable, 
            store, 
            listbox_widget):
        super().__init__(master,  **Style.left_window_frame)
        self._observable = observable
        self._store = store
       # pass
        self.tree = TreeView(
            root=root, 
            master=self, 
            observable=self._observable,
            store=self._store,
            listbox_widget=listbox_widget
        )
        # pack treeview 
        self.tree.pack(side="left", fill="both", expand=True)
        
    
    
