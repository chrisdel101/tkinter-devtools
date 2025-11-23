from __future__ import annotations
import logging
import tkinter as tk
from devtools.constants import OptionBoxState
from devtools.style import Style
from devtools.utils import Utils
from devtools.widgets.components.ConfigListboxManager import ConfigListboxManager
from devtools.widgets.windows.LeftWindowFrame import LeftWindowFrame
from devtools.widgets.windows.RightWindowFrame import RightWindowFrame

logging.basicConfig(level = logging.DEBUG)
class DevtoolsWindow(tk.Toplevel):
    def __init__(self, root, title="Devtools"):
        super().__init__(root, width=600, height=600)
        self.title(title)
        self.root = root
        self.selected_item_tree_item: tk.Widget | None = None
        # self.bind("<Button-1>", self.toggle_option_box_state)
        # right window - create first it can be passed to listbox manager as owner
        self.right_window = RightWindowFrame(master=self,
        get_tree_item_callback=self.get_current_selected_item_node, set_tree_item_callback=self.update_current_selected_item_node)

        # listbox for the config entries - sends dict of config values up when updated
        self.config_listbox_mngr = ConfigListboxManager(
            master=self.right_window, update_current_selected_item_node_callback=self.update_current_selected_item_node,toggle_option_box_state_callback=self.toggle_option_box_state,
            get_tree_item_callback=self.get_current_selected_item_node, 
            handle_subtract_callback=self.right_window.handle_subract,
            **Style.config_listbox_manager)
        # pack listbox inside right window after the fact
        self.right_window.set_listbox_manager(self.config_listbox_mngr)

        # left window - sends currently selected node up when changed - pass down listbox to apply updates
        self.left_window = LeftWindowFrame(root=root, master=self, listbox_widget=self.config_listbox_mngr, set_current_node_selected_callback=self.store_current_selected_item_node)

        # pack left window
        self.left_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # self.right_window.pack_propagate(False)
        # self.bind("<FocusOut>", lambda e: print(self.tk.call('focus')))

        
    def update_current_selected_item_node(self, changes_dict: dict[str, str]):
        self.left_window.tree.update_tree_item(changes_dict)
    # when treeview is selected store the matching app node widget 
    def store_current_selected_item_node(self, _, selected_item):
        self.selected_item_tree_item: tk.Widget | None = selected_item

    def get_current_selected_item_node(self):
        return self.selected_item_tree_item
    # toggle when open on child - detect on window and close
    # optionbox does not detect close, window does not detect open
    def toggle_option_box_state(self, event):
        if self.config_listbox_mngr.children.get("!optionmenu") != event.widget:
            return
        # if open set to closed - else set to open
        elif self.config_listbox_mngr.option_box_state == OptionBoxState.CLOSED.value:
            self.config_listbox_mngr.option_box_state = OptionBoxState.OPEN.value
            # logging.debug("Option box opened.")
        else:
            self.config_listbox_mngr.option_box_state = OptionBoxState.CLOSED.value
            # logging.debug("Option box closed.")
        logging.debug(f"state: {self.config_listbox_mngr.option_box_state}")