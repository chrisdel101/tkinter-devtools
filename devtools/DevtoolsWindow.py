from __future__ import annotations
import logging
import tkinter as tk
from devtools.constants import OptionBoxState
from devtools.style import Style
from devtools.utils import Utils
from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager
from devtools.components.widgets.windows.LeftWindowFrame import LeftWindowFrame
from devtools.components.widgets.windows.RightWindowFrame import RightWindowFrame
from devtools.components.subject_context import SubjectState

logging.basicConfig(level = logging.DEBUG)
class DevtoolsWindow(tk.Toplevel):
    def __init__(self, root, title="Devtools"):
        super().__init__(root)
        self.title(title)
        self.root = root
        self.state_subject = SubjectState()
        # state
        self.selected_item_tree_item: tk.Widget | None = None
        self.devtools_window_in_focus = True
        self.selected_combobox_wrapper: tk.Widget | None = None
        self.selected_combobox: tk.Widget | None = None
        self.active_adding: bool = False # during add new item
        # right window - create first it can be passed to listbox manager as owner
        self.right_window = RightWindowFrame(
            master=self,
            state_subject=self.state_subject,
            get_tree_item_callback=self.get_current_selected_item_node, update_current_selected_item_node_callback=self.update_current_selected_item_node)

        # listbox for the conf`ig entries - sends dict of config values up when updated
        self.config_listbox_mngr = ConfigListboxManager(
            master=self.right_window, 
            state_subject=self.state_subject,
            update_current_selected_item_node_callback=self.update_current_selected_item_node,toggle_option_box_state_callback=self.toggle_option_box_state,
            get_tree_item_callback=self.get_current_selected_item_node, 
            handle_subtract_callback=self.right_window.handle_subract,
            track_any_selected_combobox_or_wrapper_callback=self.track_any_selected_combobox_or_wrapper,
            **Style.config_listbox_manager)
        # pack listbox inside right window after the fact
        self.right_window.set_listbox_manager(self.config_listbox_mngr)

        # left window - sends currently selected node up when changed - pass down listbox to apply updates
        self.left_window = LeftWindowFrame(root=root, master=self,state_subject=self.state_subject,
         listbox_widget=self.config_listbox_mngr, set_current_node_selected_callback=self.store_current_selected_item_node)

        # pack left window
        self.left_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack right window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<FocusIn>", self.on_focus_in)
        # self.poll_for_changes()

    @property
    def active_adding(self):
        return self._active_adding

    @active_adding.setter
    def active_adding(self, value):
        print('setting active_adding to', value )
        self._active_adding = value 

    def on_focus_out(self, e):
        if self.devtools_window_in_focus:
            focus_widget = Utils._safe_focus_displayof(self)
          
            if focus_widget is None:
                logging.debug("DevtoolsWindow REALLY lost focus")
                self.devtools_window_in_focus = False
                if self.selected_combobox_wrapper:
                    pass
                    logging.debug("Focus out - cancelling comboboxes.")
                    # cancel any comboxes that are stored in state
                    self.config_listbox_mngr._cancel_update(self.selected_combobox_wrapper, *self.selected_combobox_wrapper.winfo_children())
                    self.untrack_any_selected_comboboxs_or_wrappers()
        
    def on_focus_in(self, e):
        # if state if false
        if not self.devtools_window_in_focus:
            # if focus on window
            if self.focus_displayof():
                logging.debug("focus back")
                # set state to true
                self.devtools_window_in_focus = True
    # track frame and inner combobox - when window focus out - cancel all comboboxes
    # - no focus out available in combobox itself
    def track_any_selected_combobox_or_wrapper(self,widget):
        try:
            if widget.winfo_name() == "!combobox":
                # store combobox i
                logging.debug(f"Combobox selected1 NO LOGIC: {widget.get()}")
            else:    
                for child in widget.winfo_children():
                    if child.winfo_name() == "!combobox":
                        # store wrapper if child is combobox
                        self.selected_combobox_wrapper = widget
                        self.selected_combobox = child
                        logging.debug(f"Combobox state added: {widget}")
                        break
              
        except Exception as e:
            logging.error(f"Error tracking combobox selection: {e}", exc_info=True)
    # remove any selected comboboxs or wrappers in state
    def untrack_any_selected_comboboxs_or_wrappers(self):
        if self.selected_combobox_wrapper:
            logging.debug("Combobox removed from state.", self.selected_combobox_wrapper)
            self.selected_combobox_wrapper = None
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

    def poll_for_changes(self):
        # poll tree for changes
        self.left_window.tree.collect_widgets(self.root)
        # poll again after delay
        self.after(1000, self.poll_for_changes)
        logging.debug("Polling for changes...")