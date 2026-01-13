from __future__ import annotations
import logging
from tkinter import ttk
from devtools.components.observable import Action
from devtools.constants import ActionType, ListboxPageInsertEnum, TreeStateKey
from devtools.decorators import try_except_catcher
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
        self._options_config_listbox_mngr = ConfigListboxManager(
            master=self, 
            listbox_page_insert_enum=ListboxPageInsertEnum.OPTIONS,
            observable=self._observable,
            store=self._store,           
            **Style.config_listbox_manager)
        # self._observable.register_observer(self._options_config_listbox_mngr)

        self._geometry_config_listbox_mngr = ConfigListboxManager(
            master=self, 
            listbox_page_insert_enum=ListboxPageInsertEnum.GEOMETRY,
            observable=self._observable,
            store=self._store,           
            **Style.config_listbox_manager)
        self._store.listbox_inserts = {
            ListboxPageInsertEnum.OPTIONS: self._options_config_listbox_mngr,
            ListboxPageInsertEnum.GEOMETRY: self._geometry_config_listbox_mngr  
        }
        # self._options_config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
        self._observable.register_observer(self)
        # button header
        self.header_frame = tk.Frame(self, **Style.right_window['header']['frame'])
        # top row wrappper - using wrap allows focused styling
        self.top_row_wrapper = tk.Frame(self.header_frame, **Style.right_window['header']['top_row']['frame'])
        self.top_row_wrapper.grid(row=0, column=0, sticky="w")
        # bottom row wrappper
        self.bottom_row_wrapper = tk.Frame(self.header_frame, **Style.right_window['header']['bottom_row'])
        self.bottom_row_wrapper.grid(row=1, column=0, sticky="w")

        self.attr_button = ttk.Button(self.top_row_wrapper, text=Style.right_window['header']['top_row']['option_button_text'])
        self.geo_button = ttk.Button(self.top_row_wrapper, text=Style.right_window['header']['top_row']['geo_button_text'])
        self.attr_button.bind("<Button-1>", lambda e: self.handle_pack_listbox_page_insert_click  (insert_type_enum=ListboxPageInsertEnum.OPTIONS))
        self.geo_button.bind("<Button-1>", lambda e: self.handle_pack_listbox_page_insert_click(insert_type_enum=ListboxPageInsertEnum.GEOMETRY))
       
        add_config_button = tk.Button(self.bottom_row_wrapper, text="+", command=lambda: self.handle_add(0), width=2, height=2)
        
        self.subtract_config_button = tk.Button(self.bottom_row_wrapper, text="-", command=self.handle_subtract_selection, width=2, height=2)

        self.attr_button.grid(row=0, column=0, padx=5, pady=5, sticky='sw')
        self.geo_button.grid(row=0, column=1, padx=5, pady=5, sticky='sw')
        # pack add button
        add_config_button.grid(row=1, column=0, padx=5, pady=5, sticky='sw')
        # pack subtract button
        self.subtract_config_button.grid(row=1, column=1, padx=5, pady=5, sticky='sw')
        # add focus on click - allows focus out from listbox to work
        self.header_frame.bind("<Button-1>", lambda e: self.header_frame.focus_set())
        #  pack header
        self.header_frame.pack(fill='both')
        # load _options_config_listbox_mngr listbox by default
        self.pack_listbox_page_insert(insert_type_enum=ListboxPageInsertEnum.OPTIONS)
    
    @try_except_catcher
    def toggle_geo_button_visible(self, visible: bool):
        if visible:
            Utils.show_widget(self.geo_button, self._store)
        else:
            Utils.hide_widget(self.geo_button, self._store)
    
    @try_except_catcher
    # run pack_listbox_page_insert with check to no repack same insert
    def handle_pack_listbox_page_insert_click(self, insert_type_enum: ListboxPageInsertEnum):
        # guard logic - block re-packing same listbox
        if current_listbox_insert_enum := (self._store.current_listbox_insert and self._store.current_listbox_insert._listbox_page_insert_enum):
            if current_listbox_insert_enum == insert_type_enum:
                # button clicked on current - already packed 
                return
            self._store.current_listbox_insert.pack_forget()
        self.pack_listbox_page_insert(insert_type_enum=insert_type_enum)

    @try_except_catcher
    def pack_listbox_page_insert(self, insert_type_enum: ListboxPageInsertEnum):
        match insert_type_enum:
            case ListboxPageInsertEnum.OPTIONS:
                    # set new current list
                    self._store.current_listbox_insert = self._options_config_listbox_mngr
                    self._options_config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
            case ListboxPageInsertEnum.GEOMETRY:
                    # set new current list
                    self._store.current_listbox_insert = self._geometry_config_listbox_mngr
                    self._geometry_config_listbox_mngr.pack(side="bottom", fill="both", expand=True)
            case _:
                logging.error(f"Error pack_listbox_page_insert: No listbox packed", exc_info=True)
    
    
    # add new item to listbox
    @try_except_catcher
    def handle_add(self, index=None):
        if self._store.block_active_adding:
            logging.debug("handle_add state true. Cannot add.")
            return
        # setter for state store
        self._store.block_active_adding = True
        current_listbox_insert_widget = self._store.current_listbox_insert
        current_listbox_insert_enum = ListboxPageInsertEnum
        # if current_listbox_insert_widget._listbox_page_insert_enum == ListboxPageInsertEnum.OPTIONS:
        current_listbox_selection = current_listbox_insert_widget.curselection()
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
        # insert into listbox
        current_listbox_insert_widget.insert_listbox_item(index=insert_at_index, value="")
        # init entry input process
        current_listbox_insert_widget.handle_entry_input_create(
            index=insert_at_index
        )
        
    # remove current selection
    @try_except_catcher
    def handle_subtract_selection(self, _=None):
        if self._store.block_active_adding:
            logging.debug("addning state is blocked/in session. Cannot subtract.")
            return
        current_listbox = self._store.current_listbox_insert
        # this is tuple format (3,)
        curselection: tuple[int] = current_listbox.curselection()
        # current_treeview_item = self._store.tree_state_get('selected_item')

        if len(curselection) == 0:
            print("No item selected to remove.")
            return
        else:
            current_widget = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET)
            # look up original state in memory_id store w py id
            memory_id = id(current_widget)
            mem_widget_store_dict = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
            lookup_by_id_frozen_config = mem_widget_store_dict.get(memory_id)['widget_config_init_frozen']
            
            # get value at listbox selected index
            active_item_value = current_listbox.get(tk.ACTIVE)
            # if active send blank value to undo _options_config_listbox_mngr on widget
            if active_item_value:
                listbox_item_pairs_dict = Utils.build_split_str_pairs_dict(current_listbox.get(tk.ACTIVE))
                original_config_value = lookup_by_id_frozen_config.get(listbox_item_pairs_dict['key'])
                # updates the page widget - notify tree - sets config to zero
                self._observable.notify_observers(
                    Action(type=ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET_OPTION_CONFIG, 
                    data={
                        "key": listbox_item_pairs_dict['key'],
                        "value": original_config_value
                }))   
            # unpack first item from tuple
            current_selection_index, = curselection
            # remove from listbox
            current_listbox.delete(current_selection_index)

    # remove current session by index - not yet saved to tree or page
    @try_except_catcher
    def handle_subtract_index(self, index: int):
        try:
            self._options_config_listbox_mngr.delete(index)
        except Exception as e:
            logging.error(f"Error in handle_subtract_in_session: {e}", exc_info=True)

    def notify(self, action: Action):
        Utils.dispatch_action(self, action)
       