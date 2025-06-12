from ConfigListbox import ConfigListbox
from TreeView import TreeView
from windows.WindowFrame import WindowFrame


class LeftWindowFrame(WindowFrame):
    def __init__(self, root, master=None, listbox_widget=None):
        super().__init__(master, background='orange')
       # pass the other window listbox down for updating it from left window
        self.tree = TreeView(master=master, listbox_widget=listbox_widget)
        self.tree.bind_tree_select()
        self.tree.build_tree(root)

        self.tree.select_tree_item(self.tree.get_children()[0]) 
        # pack treeview 
        self.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
       

    
