from __future__ import annotations
import tkinter as tk
from devtools.style import Style
from devtools.components.widgets.TreeView import TreeView

class LeftWindowFrame(tk.Frame):
    def __init__(self, 
            root, 
            master, 
            observable, 
            store):
        super().__init__(master,  **Style.left_window['frame'])
        self._observable = observable
        self._store = store
        self.tree = TreeView(
            root=root, 
            master=self, 
            observable=self._observable,
            store=self._store)
        # pack treeview 
        self.tree.pack(side="left", fill="both", expand=True)
        
    
    
