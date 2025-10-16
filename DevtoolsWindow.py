import tkinter as tk
from style import Style
from utils import Utils
from widgets.components.ConfigListboxManager import ConfigListboxManager
from widgets.windows.LeftWindowFrame import LeftWindowFrame
from widgets.windows.RightWindowFrame import RightWindowFrame

class DevtoolsWindow:
    def __init__(self, root, title="Devtools"):
        # Toplevel is the window itself that opens
        self.top_level = tk.Toplevel(root, background='red')
        self.top_level.title(title)
        self.root = root
        self.selected_item_tree_item: tk.Widget | None = None
        # listbox for the config entries - sends dict of config values up when updated
        k_wargs = Utils.match_safe_kwargs(widget_cls=ConfigListboxManager, master=self.top_level, **Style.config_listbox_manager)
        self.config_listbox_mngr = ConfigListboxManager(master=self.top_level, **k_wargs)
        # left window - sends currenltly selected node up when changed
        self.left_window = LeftWindowFrame(root=root, master=self.top_level, listbox_widget=self.config_listbox_mngr, set_current_node_selected_callback=self.store_current_selected_item_node)
         # right window
        self.right_window = RightWindowFrame(master=self.top_level, config_listbox_mngr=self.config_listbox_mngr,
        get_tree_item_callback=self.get_current_selected_item_node, set_tree_item_callback=self.update_current_selected_item_node)

        # pack left window
        self.left_window.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)

        
    def update_current_selected_item_node(self, _, changes_dict):
        self.left_window.tree.update_tree_item(changes_dict)
    # when treeview is selected store the matching app node widget 
    def store_current_selected_item_node(self, _, selected_item):
        self.selected_item_tree_item: tk.Widget | None = selected_item

    def get_current_selected_item_node(self):
        return self.selected_item_tree_item

