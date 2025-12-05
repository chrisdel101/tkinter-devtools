from __future__ import annotations
from devtools.style import Style
from devtools.widgets.components.TreeView import TreeView
from devtools.widgets.windows.WindowFrame import WindowFrame

class LeftWindowFrame(WindowFrame):
    def __init__(self, root, master, listbox_widget, set_current_node_selected_callback):
        super().__init__(master,  **Style.left_window_frame)
       # pass the other window listbox down for updating it from left window
        self.tree = TreeView(root=root, master=self, listbox_widget=listbox_widget)
        self.tree.bind_tree_select(set_current_node_selected_callback=set_current_node_selected_callback)
        self.tree.build_tree(root)

        self.tree.select_tree_item(self.tree.get_children()[0]) 
        # pack treeview 
        self.tree.pack(side="left", fill="both", expand=True)
        self.selected_item = None
       

    
