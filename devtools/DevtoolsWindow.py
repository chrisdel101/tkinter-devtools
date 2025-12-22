from __future__ import annotations
import logging
import tkinter as tk
from devtools.components.observable import Observable
from devtools.components.store import Store
from devtools.constants import OptionBoxState
from devtools.style import Style
from devtools.utils import Utils
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
        self._store = Store()
        # state
        self.devtools_window_in_focus = True
        self.selected_combobox_wrapper: tk.Widget | None = None
        self.selected_combobox: tk.Widget | None = None
        # right window - create first it can be passed to listbox manager as owner
        self.right_window = RightWindowFrame(
            master=self,
            observable=self._observable,
            store=self._store)

        # listbox for the conf`ig entries - sends dict of config values up when updated
        self.config_listbox_mngr = ConfigListboxManager(
            master=self.right_window, 
            observable=self._observable,
            store=self._store,            **Style.config_listbox_manager)
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
        if self.devtools_window_in_focus:
            # focus_widget = Utils._safe_focus_displayof(self)
          
            # if focus_widget is None:
            #     logging.debug("DevtoolsWindow REALLY lost focus")
                self.devtools_window_in_focus = False
                if self._store.selected_combobox_wrapper and self._store.selected_combobox_wrapper.winfo_exists():
                    # cancel any comboxes that are stored in state
                    self.config_listbox_mngr._cancel_update(self._store.selected_combobox_wrapper, *self._store.selected_combobox_wrapper.winfo_children())
                    self._store.focus_out_untrack_comboboxs_or_wrappers()
        
    def on_focus_in(self, e):
        # if state if false
        if not self.devtools_window_in_focus:
            # if focus on window
            if self.focus_displayof():
                logging.debug("focus back")
                # set state to true
                self.devtools_window_in_focus = True
    # # track frame and inner combobox - when window focus out - cancel all comboboxes
    # # - no focus out available in combobox itself
    # def track_any_selected_combobox_or_wrapper(self,widget):
    #     try:
    #         if widget.winfo_name() == "!combobox":
    #             # store combobox i
    #             logging.debug(f"Combobox selected1 NO LOGIC: {widget.get()}")
    #         else:    
    #             for child in widget.winfo_children():
    #                 if child.winfo_name() == "!combobox":
    #                     # store wrapper if child is combobox
    #                     self.selected_combobox_wrapper = widget
    #                     self.selected_combobox = child
    #                     logging.debug(f"Combobox state added: {widget}")
    #                     break
              
    #     except Exception as e:
    #         logging.error(f"Error tracking combobox selection: {e}", exc_info=True)
    # # remove any selected comboboxs or wrappers in state
    # def focus_out_untrack_comboboxs_or_wrappers(self):
    #     if self._store.selected_combobox_wrapper:
    #         logging.debug(f"Combobox removed from state.", {self._store.selected_combobox_wrapper})
    #         self._store.selected_combobox_wrapper = None
    def update_current_selected_item_node(self, changes_dict: dict[str, str]):
        self.left_window.tree.update_tree_item(changes_dict)
    
    # NOT USED- toggle when open on child - detect on window and close
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

    def poll_for_changes(self):
        # poll tree for changes
        self.left_window.tree.collect_widgets(self.root)
        # poll again after delay
        self.after(1000, self.poll_for_changes)
        logging.debug("Polling for changes...")