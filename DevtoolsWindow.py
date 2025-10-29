import tkinter as tk
from style import Style
from utils import Utils
from widgets.components.ConfigListboxManager import ConfigListboxManager
from widgets.windows.LeftWindowFrame import LeftWindowFrame
from widgets.windows.RightWindowFrame import RightWindowFrame

class DevtoolsWindow(tk.Toplevel):
    def __init__(self, root, title="Devtools"):
        super().__init__(root, width=600, height=600)
        self.title(title)
        self.root = root
        self.selected_item_tree_item: tk.Widget | None = None
        # listbox for the config entries - sends dict of config values up when updated
        self.config_listbox_mngr = ConfigListboxManager(master=self, update_current_selected_item_node_callback=self.update_current_selected_item_node, **Style.config_listbox_manager)
        # left window - sends currenltly selected node up when changed
        self.left_window = LeftWindowFrame(root=root, master=self, listbox_widget=self.config_listbox_mngr, set_current_node_selected_callback=self.store_current_selected_item_node)
         # right window
        self.right_window = RightWindowFrame(master=self, config_listbox_mngr=self.config_listbox_mngr,
        get_tree_item_callback=self.get_current_selected_item_node, set_tree_item_callback=self.update_current_selected_item_node)

        # pack left window
        # self.left_window.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        self.right_window.pack_propagate(False)
        self.bind("<FocusOut>", lambda e: print(self.tk.call('focus')))

        
    def update_current_selected_item_node(self, _, changes_dict):
        self.left_window.tree.update_tree_item(changes_dict)
    # when treeview is selected store the matching app node widget 
    def store_current_selected_item_node(self, _, selected_item):
        self.selected_item_tree_item: tk.Widget | None = selected_item

    def get_current_selected_item_node(self):
        return self.selected_item_tree_item

