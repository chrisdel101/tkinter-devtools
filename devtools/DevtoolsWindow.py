from __future__ import annotations
import logging
import tkinter as tk
from devtools.components.observable import Observable, Action
from devtools.components.store import Store
from devtools.constants import ActionType, ListBoxEntryInputAction
from devtools.style import Style
from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager
from devtools.components.widgets.windows.LeftWindowFrame import LeftWindowFrame
from devtools.components.widgets.windows.RightWindowFrame import RightWindowFrame


logging.basicConfig(level = logging.DEBUG)
class DevtoolsWindow(tk.Toplevel):
    def __init__(self, root, title="Devtools"):
        super().__init__(root)
        self.title(title)
        self.root = root
        self._observable = Observable()
        self._store = Store(observable=self._observable)
        # state
        # right window - create first it can be passed to listbox manager as owner
        self.right_window = RightWindowFrame(
            master=self,
            observable=self._observable,
            store=self._store)

        # listbox for the conf`ig entries - sends dict of config values up when updated
        self.config_listbox_mngr = ConfigListboxManager(
            master=self.right_window, 
            observable=self._observable,
            store=self._store,           
            **Style.config_listbox_manager)
        # pack listbox inside right window after the fact
        self.right_window.set_listbox_manager(self.config_listbox_mngr)

        # left window - sends currently selected node up when changed - pass down listbox to apply updates
        self.left_window = LeftWindowFrame(
            root=root, 
            master=self,
            observable=self._observable,
            store=self._store,
            listbox_widget=self.config_listbox_mngr)

        # pack left window
        self.left_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)

        self.bind("<Deactivate>", self.on_focus_out)
        self.bind("<FocusIn>", self.on_focus_in)
        # self.poll_for_changes()


    def on_focus_out(self, e):
        if self._store.devtools_window_in_focus:
            self._store.devtools_window_in_focus = False
            if len(self._store.existing_combobox_wrappers) > 0:
                # remove all comboxes from the page
                self.config_listbox_mngr.cancel_update_listbox(*self._store.existing_combobox_wrappers)
                # remove all comboxes from state
                self._store.remove_existing_store_wrappers()
                if self._store.listbox_entry_input_action == ListBoxEntryInputAction.CREATE:
                    self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX.name, data=0))
                self._store.block_active_adding = False
        
    def on_focus_in(self, e):
        # if state if false
        if not self._store.devtools_window_in_focus:
            # if focus on window
            if self.focus_displayof():
                logging.debug("focus back")
                # set state to true
                self._store.devtools_window_in_focus = True
    
    # def update_current_selected_item_node(self, changes_dict: dict[str, str]):
    #     self.left_window.tree.update_tree_item(changes_dict)
    

    def poll_for_changes(self):
        # poll tree for changes
        self.left_window.tree.collect_widgets(self.root)
        # poll again after delay
        self.after(1000, self.poll_for_changes)
        logging.debug("Polling for changes...")