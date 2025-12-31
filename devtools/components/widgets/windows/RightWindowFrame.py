from __future__ import annotations
import logging
from tkinter import ttk
from unittest import case
from devtools.components.observable import Action
from devtools.constants import ActionType, ListboxManagerStateKey, ListboxPageInsertType, TreeStateKey
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
        self._attr_config_listbox_mngr = ConfigListboxManager(
            master=self, 
            listbox_page_insert_type=ListboxPageInsertType.ATTRIBUTES,
            observable=self._observable,
            store=self._store,           
            **Style.config_listbox_manager)
        # self._observable.register_observer(self._attr_config_listbox_mngr)

        self._geometry_config_listbox_mngr = ConfigListboxManager(
            master=self, 
            listbox_page_insert_type=ListboxPageInsertType.GEOMETRY,
            observable=self._observable,
            store=self._store,           
            **Style.config_listbox_manager)
        # self._attr_config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
        self._observable.register_observer(self)
        # button header
        self.header_frame = tk.Frame(self, **Style.right_window['header']['frame'])
        # top row wrappper - using wrap allows focused styling
        self.top_row_wrapper = tk.Frame(self.header_frame, **Style.right_window['header']['top_row']['frame'])
        self.top_row_wrapper.grid(row=0, column=0, sticky="w")
        # bottom row wrappper
        self.bottom_row_wrapper = tk.Frame(self.header_frame, **Style.right_window['header']['bottom_row'])
        self.bottom_row_wrapper.grid(row=1, column=0, sticky="w")

        attr_button = ttk.Button(self.top_row_wrapper, text=Style.right_window['header']['top_row']['attr_button_text'])
        geo_button = ttk.Button(self.top_row_wrapper, text=Style.right_window['header']['top_row']['geo_button_text'])
        attr_button.bind("<Button-1>", lambda e: self.pack_listbox_page_insert  (insert_type=ListboxPageInsertType.ATTRIBUTES))
        geo_button.bind("<Button-1>", lambda e: self.manual_pack_listbox_page_insert(insert_type=ListboxPageInsertType.GEOMETRY))
       
        self.add_config_button = tk.Button(self.bottom_row_wrapper, text="+", command=lambda:self.handle_add(index=0), width=2, height=2)
        
        self.subtract_config_button = tk.Button(self.bottom_row_wrapper, text="-", command=self.handle_subtract_selection, width=2, height=2)

        attr_button.grid(row=0, column=0, padx=5, pady=5, sticky='sw')
        geo_button.grid(row=0, column=1, padx=5, pady=5, sticky='sw')
        # pack add button
        self.add_config_button.grid(row=1, column=0, padx=5, pady=5, sticky='sw')
        # pack subtract button
        self.subtract_config_button.grid(row=1, column=1, padx=5, pady=5, sticky='sw')
        # add focus on click - allows focus out from listbox to work
        self.header_frame.bind("<Button-1>", lambda e: self.header_frame.focus_set())
        #  pack header
        self.header_frame.pack(fill='both')
        # load attr listbox by default
        self.pack_listbox_page_insert(insert_type=ListboxPageInsertType.ATTRIBUTES)
    
    def pack_listbox_page_insert(self, insert_type: ListboxPageInsertType):
        try:
            if self._store.current_listbox_insert:
                self._store.current_listbox_insert.pack_forget()
            match insert_type:
                case ListboxPageInsertType.ATTRIBUTES:
                     self._store.current_listbox_insert = self._attr_config_listbox_mngr
                     self._attr_config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
                case ListboxPageInsertType.GEOMETRY:
                     print("XXX")
                     self._store.current_listbox_insert = self._geometry_config_listbox_mngr
                     self._store.listbox_manager_state_set(enum_key=ListboxManagerStateKey.CURRENT_VALUES_STATE, state_to_set={"hello":f"{self._store.current_listbox_insert.listbox_page_insert_type}"})
                     self._geometry_config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
                case _:
                    logging.error(f"Error pack_listbox_page_insert: No listbox packed", exc_info=True)
            pass
        except Exception as e:
            logging.error(f"Error pack_listbox_page_insert: {e}", exc_info=True)
    
    def manual_pack_listbox_page_insert(self, insert_type: ListboxPageInsertType):
        try:
            if self._store.current_listbox_insert:
                self._store.current_listbox_insert.pack_forget()
            print("XXX")
            self._store.current_listbox_insert = self._geometry_config_listbox_mngr
            self._store.listbox_manager_state_set(enum_key=ListboxManagerStateKey.CURRENT_VALUES_STATE, state_to_set={"hello":f"{self._store.current_listbox_insert.listbox_page_insert_type}"})
            self._geometry_config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
        except Exception as e:
            logging.error(f"Error pack_listbox_page_insert: {e}", exc_info=True)
    # add new item to listbox
    def handle_add(self, index=None):
        if self._store.block_active_adding:
            logging.debug("handle_add state true. Cannot add.")
            return
        # setter for state store
        self._store.block_active_adding = True
        current_listbox_selection = self._attr_config_listbox_mngr.curselection()
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
        self._attr_config_listbox_mngr.insert_listbox_item(index=insert_at_index, value="")
        # called on the child listbox
        self._attr_config_listbox_mngr.handle_entry_input_create(
            index=insert_at_index
        )
        
    # remove current selection
    def handle_subtract_selection(self, _=None):
        if self._store.block_active_adding:
            logging.debug("addning state is blocked/in session. Cannot subtract.")
            return
        # this is tuple format (3,)
        curselection: tuple[int] = self._attr_config_listbox_mngr.curselection()
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
            active_item_value =self._attr_config_listbox_mngr.get(tk.ACTIVE)
            # if active send blank value to undo attr on widget
            if active_item_value:
                changes_dict = Utils.build_split_str_pairs_dict(self._attr_config_listbox_mngr.get(tk.ACTIVE))
                original_config_value = lookup_by_id_frozen_config.get(changes_dict['key'])
                # updates the page widget - notify tree - sets config to zero
                self._observable.notify_observers(
                    Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET, 
                    data={
                        "key": changes_dict['key'],
                        "value": original_config_value
                }))   
            # unpack first item from tuple
            current_selection_index, = curselection
            # remove from listbox
            self._attr_config_listbox_mngr.delete(current_selection_index)

    # remove current session by index - not yet saved to tree or page
    def handle_subtract_index(self, index: int):
        try:
            self._attr_config_listbox_mngr.delete(index)
        except Exception as e:
            logging.error(f"Error in handle_subtract_in_session: {e}", exc_info=True)

    def notify(self, action: Action):
        Utils.dispatch_action(self, action)
       