from __future__ import annotations
import logging
import tkinter as tk
from devtools.components.observable import Observable, Action
from devtools.components.store import Store
from devtools.constants import ActionType, CustomLogLevel, ListBoxEntryInputAction
from devtools.decorators import try_except_catcher
from devtools.components.widgets.windows.LeftWindowFrame import LeftWindowFrame
from devtools.components.widgets.windows.RightWindowFrame import RightWindowFrame
from devtools.config import kwargs_config, app_config
from devtools.logging_utils import LoggingUtils
from devtools.tcl_runtime_utils import TclRunTimeUtility


class DevtoolsWindow(tk.Toplevel):
    def __init__(self, root, title=app_config['app_title'], **kwargs):
        super().__init__(root, name=app_config['top_level_name'])
        # run to update page render for before tree maps
        root.update_idletasks()
        # run runtime checks of tcl bridge
        TclRunTimeUtility.runtime_checks(root)     
        # overwrite any default config with kwargs
        kwargs_config.update(**kwargs)
        # set logging level
        LoggingUtils.set_logging_level(CustomLogLevel.TRACE.value)
        self.title(title)
        self.root = root
        self._observable = Observable()
        self._store = Store(root=root, observable=self._observable, config=kwargs_config)
        
        self.left_window = LeftWindowFrame(
            root=root, 
            parent=self,
            observable=self._observable,
            store=self._store)
    
        self.right_window = RightWindowFrame(
            parent=self,
            observable=self._observable,
            store=self._store)
        # pack left window
        self.left_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)

        self.bind("<Deactivate>", self.on_focus_out)
        self.bind("<FocusIn>", self.on_focus_in)
        self.geometry("+700+0")
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
                logging.trace("focus back")
                # set state to true
                self._store.devtools_window_in_focus = True

    def poll_for_changes(self):
        # poll tree for changes
        self.left_window.tree.collect_widgets(self.root)
        # poll again after delay
        self.after(1000, self.poll_for_changes)
        logging.debug("Polling for changes...")