from __future__ import annotations
import logging
from devtools.components.observable import Action
from devtools.constants import ActionType
from devtools.style import Style
from devtools.utils import Utils
from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager
import tkinter as tk

class RightWindowFrame(tk.Frame):
    def __init__(self, 
                master, 
                observable, 
                store 
                ):
        super().__init__(master, **Style.right_window_frame)
        self._observable = observable
        self._store = store
        self._observable.register_observer(self)
        # button header
        self.header_frame = tk.Frame(self, **Style.header)
       
        self._config_listbox_mngr: ConfigListboxManager = None
        self.add_config_button = tk.Button(self.header_frame, text="+", command=lambda:self.handle_add(index=0), width=2, height=2)
        self.subtract_config_button = tk.Button(self.header_frame, text="-", command=self.handle_subtract_selection, width=2, height=2)
        # pack add button
        self.add_config_button.pack(side="left", padx=5, pady=5,anchor='sw')
        # pack subtract button
        self.subtract_config_button.pack(side="left", padx=5, pady=5, anchor='sw')
        # add focus on click - allows focus out from listbox to work
        self.header_frame.bind("<Button-1>", lambda e: self.header_frame.focus_set())
        #  pack header
        self.header_frame.pack(fill='both', expand=True)
        
    # add listbox manager after init - b/c right window parent is master but both r sitting side by side
    def set_listbox_manager(self, config_listbox_mngr):
        setattr(self, '_config_listbox_mngr', config_listbox_mngr)
        self._config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
    def handle_add(self, index=None):
        # self.add_config_button.state = "disabled"
        print("HERE1", self._store.block_active_adding)
        print("HEREX", index)
       
       

        if self._store.block_active_adding:
            logging.debug("handle_add state true. Cannot add.")
            return
        # setter for state store
        self._store.block_active_adding = True
        current_listbox_selection = self._config_listbox_mngr.curselection()
        # current_treeview_item = self._store.tree_state_get('selected_item')
        if index is not None:
            insert_at_index = index
        elif len(current_listbox_selection) == 0:
            # if none selected insert at top
            insert_at_index = 0
        else:
            # insert after selected_item
            current_selection_index = current_listbox_selection[0]
            insert_at_index = current_selection_index + 1
        print("Inserting at index:", insert_at_index)
        self._config_listbox_mngr.insert(insert_at_index, "")
        # called on the child listbox
        self._config_listbox_mngr.handle_entry_input_create(
            index=insert_at_index
        )
        
    # remove current selection or remove by index if added
    def handle_subtract_selection(self, e=None, custom_index: int = None):
        # this is tuple format (3,)
        curselection: tuple[int] = self._config_listbox_mngr.curselection()
        # current_treeview_item = self._store.tree_state_get('selected_item')

        if len(curselection) == 0:
            print("No item selected to remove.")
            return
        else:
            # get value at listbox selected index
            active_item_value =self._config_listbox_mngr.get(tk.ACTIVE)
            # if active send blank value to undo attr on widget
            if active_item_value:
                changes_dict = Utils.build_split_str_pairs_dict(self._config_listbox_mngr.get(tk.ACTIVE))
                # updates the page widget - notify tree - sets config to zero
                self._observable.notify_observers(
                    Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET.name, 
                    data={
                        "key": changes_dict['key'],
                        "value": ""
                }))   
            # unpack first item from tuple
            current_selection_index, = curselection if not custom_index else (custom_index,)
            # remove from listbox
            self._config_listbox_mngr.delete(current_selection_index)

    # remove current session by index - not yet saved to tree or page
    def handle_subtract_index(self, index: int):
        try:
            self._config_listbox_mngr.delete(index)
        except Exception as e:
            logging.error(f"Error in handle_subtract_in_session: {e}", exc_info=True)

    def notify(self, action: Action):
        Utils.dispatch_action(self, action)
       