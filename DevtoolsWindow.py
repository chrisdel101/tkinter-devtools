import tkinter as tk
from widgets.components.ConfigListboxManager import ConfigListboxManager
from widgets.windows.LeftWindowFrame import LeftWindowFrame
from widgets.windows.RightWindowFrame import RightWindowFrame

class DevtoolsWindow:
    def __init__(self, root, title="Devtools"):
        # Toplevel is the window itself that opens
        self.top_level = tk.Toplevel(root, background='red')
        self.top_level.title(title)
        self.root = root
        # listbox for the config entries - sends dict of config values up when updated
        self.config_listbox_mngr = ConfigListboxManager(master=self.top_level, width=50, set_node_selected_callback=self.set_current_treeview_node_selected)
        # left window - sends currenltly selected node up when changed
        self.left_window = LeftWindowFrame(root=root, master=self.top_level, listbox_widget=self.config_listbox_mngr, set_current_node_selected_callback=self.set_current_treeview_node_selected)
        # right window
        self.right_window = RightWindowFrame(master=self.top_level, config_listbox_mngr=self.config_listbox_mngr,
        get_tree_item_callback=self.get_current_treeview_node_selected, set_tree_item_callback=self.set_tree_item_from_entry_value)

        # pack left window
        self.left_window.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)

        
    def set_tree_item_from_entry_value(self, _, changes_dict):
        self.left_window.tree.update_tree_item(changes_dict)
    # on treeview select item call and store the selected node
    def set_current_treeview_node_selected(self, _, selected_item):
        self.selected_item = selected_item

    def get_current_treeview_node_selected(self):
        return self.selected_item

