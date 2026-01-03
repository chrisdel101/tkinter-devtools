from __future__ import annotations
import logging
import tkinter as tk
from devtools.components.observable import Observable, Action
from devtools.components.store import Store
from devtools.constants import ActionType, ListBoxEntryInputAction
from devtools.decorators import try_except_catcher
from devtools.style import Style
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
        
        self.left_window = LeftWindowFrame(
            root=root, 
            master=self,
            observable=self._observable,
            store=self._store)
    
        self.right_window = RightWindowFrame(
            master=self,
            observable=self._observable,
            store=self._store)
        # pack left window
        self.left_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)

        self.bind("<Deactivate>", self.on_focus_out)
        self.bind("<FocusIn>", self.on_focus_in)
        # self.poll_for_changes()

    @try_except_catcher
    def on_focus_out(self, _):
        if self._store.devtools_window_in_focus:
            self._store.devtools_window_in_focus = False
            if len(self._store.existing_combobox_wrappers) > 0:
                self._observable.notify_observers(Action(type=ActionType.CANCEL_UPDATE_LISTBOX,
                    data=self._store.existing_combobox_wrappers))
                # remove all comboxes from the page
                # self.config_listbox_mngr.cancel_update_listbox(*self._store.existing_combobox_wrappers)
                # remove all comboxes from state
                self._store.remove_existing_store_wrappers()
                if self._store.listbox_entry_input_action == ListBoxEntryInputAction.CREATE:
                    self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=0))
                self._store.block_active_adding = False
        
    @try_except_catcher
    def on_focus_in(self, _):
        # if state if false
        if not self._store.devtools_window_in_focus:
            # if focus on window
            if self.focus_displayof():
                logging.debug("focus back")
                # set state to true
                self._store.devtools_window_in_focus = True

    def poll_for_changes(self):
        # poll tree for changes
        self.left_window.tree.collect_widgets(self.root)
        # poll again after delay
        self.after(1000, self.poll_for_changes)
        logging.debug("Polling for changes...")