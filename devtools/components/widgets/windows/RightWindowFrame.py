from __future__ import annotations
import logging
from tkinter import ttk
from devtools.components.observable import Action
from devtools.constants import ActionType, TreeStateKey
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
        super().__init__(master, **Style.right_window['frame'])
        self._observable = observable
        self._store = store
        self._observable.register_observer(self)
        # button header
        self.header_frame = tk.Frame(self, **Style.right_window['header']['frame'])

        self.top_row = tk.Frame(self.header_frame, **Style.right_window['header']['top_row']['frame'])
        self.top_row.grid(row=0, column=0, sticky="w")

        self.bottom_row = tk.Frame(self.header_frame, **Style.right_window['header']['bottom_row'])
        self.bottom_row.grid(row=1, column=0, sticky="w")

        btn1 = ttk.Button(self.top_row, text=Style.right_window['header']['top_row']['btn1_text'])
        btn2 = ttk.Button(self.top_row, text=Style.right_window['header']['top_row']['btn2_text'])
       
        self._config_listbox_mngr: ConfigListboxManager = None
        self.add_config_button = tk.Button(self.bottom_row, text="+", command=lambda:self.handle_add(index=0), width=2, height=2)
        
        self.subtract_config_button = tk.Button(self.bottom_row, text="-", command=self.handle_subtract_selection, width=2, height=2)

        btn1.grid(row=0, column=0, padx=5, pady=5, sticky='sw')
        btn2.grid(row=0, column=1, padx=5, pady=5, sticky='sw')
        # pack add button
        self.add_config_button.grid(row=1, column=0, padx=5, pady=5, sticky='sw')
        # pack subtract button
        self.subtract_config_button.grid(row=1, column=1, padx=5, pady=5, sticky='sw')
        # add focus on click - allows focus out from listbox to work
        self.header_frame.bind("<Button-1>", lambda e: self.header_frame.focus_set())
        #  pack header
        self.header_frame.pack(fill='both')
        
    # add listbox manager after init - b/c right window parent is master but both r sitting side by side
    def set_listbox_manager(self, config_listbox_mngr):
        setattr(self, '_config_listbox_mngr', config_listbox_mngr)
        self._config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
    def handle_add(self, index=None):
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
        self._config_listbox_mngr.insert_listbox_item(insert_at_index, "")
        # called on the child listbox
        self._config_listbox_mngr.handle_entry_input_create(
            index=insert_at_index
        )
        
    # remove current selection
    def handle_subtract_selection(self, _=None):
        if self._store.block_active_adding:
            logging.debug("addning state is blocked/in session. Cannot subtract.")
            return
        # this is tuple format (3,)
        curselection: tuple[int] = self._config_listbox_mngr.curselection()
        # current_treeview_item = self._store.tree_state_get('selected_item')

        if len(curselection) == 0:
            print("No item selected to remove.")
            return
        else:
            current_widget = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM)
            # look up original state in memory_id store w py id
            memory_id = id(current_widget)
            mem_widget_store_dict = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
            lookup_by_id_frozen_config = mem_widget_store_dict.get(memory_id)['widget_config_init_frozen']
            
            # get value at listbox selected index
            active_item_value =self._config_listbox_mngr.get(tk.ACTIVE)
            # if active send blank value to undo attr on widget
            if active_item_value:
                changes_dict = Utils.build_split_str_pairs_dict(self._config_listbox_mngr.get(tk.ACTIVE))
                original_config_value = lookup_by_id_frozen_config.get(changes_dict['key'])
                # updates the page widget - notify tree - sets config to zero
                self._observable.notify_observers(
                    Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET.name, 
                    data={
                        "key": changes_dict['key'],
                        "value": original_config_value
                }))   
            # unpack first item from tuple
            current_selection_index, = curselection
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
       