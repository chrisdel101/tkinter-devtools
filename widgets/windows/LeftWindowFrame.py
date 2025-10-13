from widgets.components.ConfigListboxManager import ConfigListboxManager
from widgets.components.TreeView import TreeView
from widgets.windows.WindowFrame import WindowFrame


class LeftWindowFrame(WindowFrame):
    def __init__(self, root, master, listbox_widget, set_current_node_selected_callback):
        super().__init__(master, background='orange')
       # pass the other window listbox down for updating it from left window
        self.tree = TreeView(master=master, listbox_widget=listbox_widget)
        self.tree.bind_tree_select(set_current_node_selected_callback=set_current_node_selected_callback)
        self.tree.build_tree(root)

        self.tree.select_tree_item(self.tree.get_children()[0]) 
        # pack treeview 
        self.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        self.selected_item = None
       

    
