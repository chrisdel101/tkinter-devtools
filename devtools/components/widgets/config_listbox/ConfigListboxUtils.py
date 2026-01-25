import logging
import tkinter as tk
from tkinter import ttk

from devtools.components.observable import Action
from devtools.constants import ActionType, ConfigOptionMapSetting, ListBoxEntryInputAction, ListboxItemState, TreeStateKey
from devtools.decorators import try_except_catcher
from devtools.maps import CONFIG_OPTION_SETTINGS, GRID_GEOMETRY_CONFIG_SETTING_VALUES, PACK_GEOMETRY_CONFIG_SETTING_VALUES, PLACE_GEOMETRY_CONFIG_SETTING_VALUES
from devtools.style import Style
from devtools.utils import Utils

class ConfigListboxUtils:
    @try_except_catcher
    def build_value_spin_box(self, 
        index: int,
        key_entry_widget: tk.Entry | ttk.Combobox,
        key_entry_value: str, 
        current_option_value: str):        
        spinbox = tk.Spinbox(self.spin_box_wrapper, 
            from_=current_option_value or 0,
            to=9999, 
            increment=1,
            textvariable=self.spinbox_var,
            **Style.config_listbox_manager['entry'])
        spinbox.bind('<Return>', lambda _: (self.insert_value_output_and_apply_to_page
                (value_entry_widget=spinbox, 
                key_entry_value=key_entry_value,
                updated_option_value=spinbox.get(), 
                ),
                setattr(self._store, 'listbox_entry_input_action', None),
                # reset spinbox var
                setattr(self, 'spinbox_var', None)
                
            ))
        spinbox.bind("<Escape>", lambda e: (
            self.cancel_update_listbox(self.key_box_wrapper, self.spin_box_wrapper), 
            # subract added item on create
            self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=0))
             if self._store.listbox_entry_input_action == ListBoxEntryInputAction.CREATE else None,
            
            setattr(self._store, 'block_active_adding', False),
            setattr(self._store, 'allow_input_focus_out_logic', True),
            setattr(self._store, 'listbox_entry_input_action', None),
             # reset spinbox var
            setattr(self, 'spinbox_var', None),
            logging.trace("spinbox escape")
            )
        )
        spinbox.bind("<FocusOut>", lambda e: (
                    logging.trace("----spinbox focus out----"),
                    self.cancel_update_listbox(*self._store.existing_combobox_wrappers),
                     self.listbox_value_focus_out(e, *self._store.existing_combobox_wrappers),
                    setattr(self._store, 'block_active_adding', False)))
        return spinbox

    @try_except_catcher
    def build_value_option_box(self, 
        index: int,
        key_entry_widget: tk.Entry | ttk.Combobox,
        key_entry_value: str,
        item_option_vals_list: list[str]
    ):
        value_inside = tk.StringVar()
        # set default top value
        value_inside.set(item_option_vals_list[0] if item_option_vals_list else "")
        # set any list to list var - done to keep it the same across calls
        self.list_var.set(item_option_vals_list or [])
        self.value_box_wrapper = tk.Frame(self.master)
        # like bind - get selected value from drop down
        value_combobox = ttk.Combobox(self.value_box_wrapper,
            textvariable=value_inside,
            values=self.list_var.get(),
            )
        for event in ["<<ComboboxSelected>>", "<Return>"]:
            value_combobox.bind(event, 
                lambda _: (self.insert_value_output_and_apply_to_page
                (value_entry_widget=value_combobox, 
                key_entry_value=key_entry_value,
                updated_option_value=value_inside.get(), 
                ),
                setattr(self._store, 'listbox_entry_input_action', None)
            ))
      
        value_combobox.bind("<Escape>", lambda e: (
            self.cancel_update_listbox(self.key_box_wrapper, self.value_box_wrapper), 
            logging.trace('combobox value escape'),
            self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=0)) if self._store.listbox_entry_input_action == ListBoxEntryInputAction.CREATE else None,
            setattr(self._store, 'block_active_adding', False),
            setattr(self._store, 'allow_input_focus_out_logic', True),
            setattr(self._store, 'listbox_entry_input_action', None)
            )
        )
        
        value_combobox.bind("<Button-1>", self.handle_value_combobox_open)
        # exists when open
        popdown = self.tk.call("ttk::combobox::PopdownWindow", value_combobox)
        # unmap fires when widget is removed or hidden
        self.tk.call(
            "bind",
            popdown,
            "<Unmap>",
            self.register(self.handle_value_combobox_closed)
        )
        value_combobox.bind("<FocusOut>", lambda e: 
                (self.listbox_value_focus_out(e, *self._store.existing_combobox_wrappers), logging.trace("combobox value focus out")))

        return value_combobox
        
    @try_except_catcher
    def build_key_option_box(self, 
        index: int,
        item_option_vals_list: list[str]):
        try:
            value_inside = tk.StringVar()
            self.key_box_wrapper = tk.Frame(self.master)
            # set default top value
            value_inside.set(item_option_vals_list[0] if item_option_vals_list else "")
            # set any list to list var - done to keep it the same across calls
            self.list_var.set(item_option_vals_list or [])
            # like bind - get selected value from drop down
            key_combo_box = ttk.Combobox(self.key_box_wrapper,
                textvariable=value_inside,
                values=self.list_var.get(),
            )
            # on select - build and pack value option box if list values
            for event in ["<<ComboboxSelected>>", "<Return>"]:
                key_combo_box.bind(event, 
                lambda _: ( 
                    self.handle_build_value_option_box_from_key_option_box( 
                        index=index,
                        key_option_box=key_combo_box,
                    value_inside=value_inside,
                    item_option_vals_list=config_setting_map.get('values')
                ) 
                if 
                  # if mapped option values send to combobox
                    (config_setting_map := self.map_config_option_to_setting(value_inside.get())) and config_setting_map.get('values')
                else 
                    # if non-mapped option values entry or spinbox
                    self.handle_build_value_entry_from_key_entry(
                    index=index,
                    key_entry_widget=key_combo_box,
                    key_entry_value=value_inside.get(),
                    y_coord=0,    
                    config_setting_map=config_setting_map,    # actual value of config option   
                    current_option_val=Utils.conform_option_lisbox_config(self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET).config()).get(value_inside.get()),
                    entry_input_action=ListBoxEntryInputAction.CREATE.value
                )
            ))            
            # this is when adding new line with new key item entry - subtract list item and cancel option box
            key_combo_box.bind("<Escape>", lambda _: 
                    (self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=index)), 
                self.cancel_update_listbox(self.key_box_wrapper),
                logging.trace("---keybox escape----"),
                setattr(self._store, 'block_active_adding', False))) 
            # use native tcl to detect when open
            key_combo_box.bind("<Button-1>", self.handle_key_combobox_open)
            # exists when open
            popdown = self.tk.call("ttk::combobox::PopdownWindow", key_combo_box)
            # unmap fires when widget is removed or hidden
            self.tk.call(
                "bind",
                popdown,
                "<Unmap>",
                self.register(self.handle_key_combobox_closed)
            )
            key_combo_box.bind("<FocusOut>", lambda e: 
                (self.listbox_key_focus_out(e, self.key_box_wrapper), logging.trace("key focus out")))
         
            return key_combo_box
        except Exception as e:
            logging.error("Error building key option box.", exc_info=True)
    # if open flip state to closed - called on tcl unmap
    def handle_key_combobox_closed(self):
        try:
            if self._store.key_combobox_popdown_open:
                self._store.key_combobox_popdown_open = False
                logging.low_trace(f"Combobox popdown closed state: {self._store.key_combobox_popdown_open}")
        except Exception as e:
            logging.error(f"Error handle_key_combobox_closed: {e}", exc_info=True)
    # when arrow clicked flip to open
    def handle_key_combobox_open(self, e):
        try:
            check = Utils.is_combobox_arrow(e.widget, e.x)
            if check:
                if not self._store.key_combobox_popdown_open:
                    self._store.key_combobox_popdown_open = True
                logging.low_trace(f"handle_key_combobox_open open state: {self._store.key_combobox_popdown_open}")
        except Exception as e:
            logging.error(f"Error handle_key_combobox_open: {e}", exc_info=True)

    # if open flip state to closed - called on tcl unmap
    def handle_value_combobox_closed(self):
        try:
            if self._store.value_combobox_popdown_open:
                self._store.value_combobox_popdown_open = False
                logging.low_trace(f"Combobox popdown closed state: {self._store.value_combobox_popdown_open}")
        except Exception as e:
            logging.error(f"Error handle_value_combobox_closed: {e}",   exc_info=True)
    # when arrow clicked flip to open
    def handle_value_combobox_open(self, e):
        try:
            check = Utils.is_combobox_arrow(e.widget, e.x)
            if check:
                if not self._store.value_combobox_popdown_open:
                    self._store.value_combobox_popdown_open = True
                logging.low_trace   (f"handle_value_combobox_open open state: {self._store.value_combobox_popdown_open}")
        except Exception as e:
            logging.error(f"Error handle_value_combobox_open: {e}", exc_info=True)

    def listbox_key_focus_out(self,e, *args):
        if self._store.key_combobox_popdown_open: 
            logging.trace(f"key LISTBOX_ON_FOCUS guard1 open")
            return
        if not self._store.allow_input_focus_out_logic:
            logging.trace(f"key LISTBOX_ON_FOCUS guard2 off {self._store.allow_input_focus_out_logic}")
            return  # internal focus change → ignore
        self._store.block_active_adding =  False
        self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=0))
        setattr(self._store, 'listbox_entry_input_action', None)
        logging.trace("listbox_key_focus_out block_active_adding setting to false")

        self.cancel_update_listbox(*args)

    def listbox_value_focus_out(self,e, *args):
        logging.trace(f"listbox_value_focus_out: {e.widget}")
        # if not self._store.allow_input_focus_out_logic:
        #     logging.trace(f"value LISTBOX_ON_FOCUS guard1 {self._store.allow_input_focus_out_logic}")
        #     return  # internal focus change → ignore
        if self._store.value_combobox_popdown_open: 
            logging.trace("value LISTBOX_ON_FOCUS guard2")
            return
        self._store.block_active_adding =  False
        self._store.allow_input_focus_out_logic = True
        if self._store.listbox_entry_input_action == ListBoxEntryInputAction.CREATE:
            self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT_INDEX, data=0))
        setattr(self._store, 'listbox_entry_input_action', None)
        self.cancel_update_listbox(*args)
    # map geometry options to any possible setting vals
    @staticmethod
    @try_except_catcher
    def map_grid_geometry_option_to_setting(option_name: str=None) -> ConfigOptionMapSetting:
        if not option_name:
            return 
        # check for options in map
        options_map_setting: ConfigOptionMapSetting|None = GRID_GEOMETRY_CONFIG_SETTING_VALUES.get(option_name)
        if options_map_setting is None:
            logging.debug(f"No mapping at all for {option_name}", exc_info=True)
        elif options_map_setting.get('values') is None:
            logging.debug(f"No relevant mapping for{option_name}", exc_info=True)
        return options_map_setting or {}
    
    # map geometry options to any possible setting vals
    @staticmethod
    @try_except_catcher
    def map_pack_geometry_option_to_setting(option_name: str=None) -> ConfigOptionMapSetting:
        if not option_name:
            return 
        # check for options in map
        options_map_setting: ConfigOptionMapSetting|None = PACK_GEOMETRY_CONFIG_SETTING_VALUES.get(option_name)
        if options_map_setting is None:
            logging.debug(f"No mapping at all for {option_name}", exc_info=True)
        elif options_map_setting.get('values') is None:
            logging.debug(f"No relevant mapping for{option_name}", exc_info=True)
        return options_map_setting or {}
    
    @staticmethod
    @try_except_catcher
    def map_place_geometry_option_to_setting(option_name: str=None) -> ConfigOptionMapSetting:
        if not option_name:
            return 
        # check for options in map
        options_map_setting: ConfigOptionMapSetting|None = PLACE_GEOMETRY_CONFIG_SETTING_VALUES.get(option_name)
        if options_map_setting is None:
            logging.debug(f"No mapping at all for {option_name}", exc_info=True)
        elif options_map_setting.get('values') is None:
            logging.debug(f"No relevant mapping for{option_name}", exc_info=True)
        return options_map_setting or {}
    
    # map widget config option to any possible setting vals - colors, positions, etc. WIll be single dict
    @staticmethod
    @try_except_catcher
    def map_config_option_to_setting(option_name: str=None) -> ConfigOptionMapSetting:
        if not option_name:
            return 
        # check for options in map
        options_map_setting: ConfigOptionMapSetting|None = CONFIG_OPTION_SETTINGS.get(option_name)
        if options_map_setting is None:
            logging.debug(f"No mapping at all for {option_name}", exc_info=True)
        elif options_map_setting.get('values') is None:
            logging.debug(f"No relevant mapping for{option_name}", exc_info=True)
        return options_map_setting or {}
    
    @staticmethod
    def cancel_update_listbox(*args):
        # args[2].destroy()
        for arg in filter(None, args):
            arg.destroy()
    
    # on init - load selected tree items options into listbox
    # runs from treeview
    def insert_listbox_items(self, **config_dict):
        try:
            for key in config_dict:
                # insert selected node into styles_window_listbox window
                display = f"{key}: {config_dict[key]}"
                # this auto sizes w/o adding styles
                # end inserts at the end of the LB
                self.insert_listbox_item(index=tk.END, key=key, value=display)
                
        except Exception as e:
            logging.error(f"Error insert_listbox_items: {e}", exc_info=True)
    # kwargs is index, value
    @try_except_catcher
    def insert_listbox_item(self, **kwargs):
        index, value = kwargs.get('index'), kwargs.get('value')
        # insert lb item
        self.insert(index, value)
        
        state = self.check_maps_for_state(**kwargs)
        # grey out any read only items
        if state == ListboxItemState.READ_ONLY:
            self.itemconfig(index, **Style.config_listbox_manager.get("item-disabled"))
    
    # use state value if map has one - used to set state in the UI
    def check_maps_for_state(self, **kwargs) -> ListboxItemState | None:
        # resolve any aliases
        resolved = Utils.listbox_option_alias_resolver(kwargs.get('key'))
        
        state = self.config_map_merge.get(resolved).get('state') if self.config_map_merge.get(resolved) else None
        # grey out any read only items
        return state

    # delete all items from listbox
    def delete_all_listbox_items(self):
        self.delete(0, tk.END)

    def _set_selected_by_index(self, index:int):
        # clear other selections
        self.selection_clear(0, "end")
        # select row
        self.selection_set(index)
        # activate on keyboard
        self.activate(index)

    def listbox_in_parent_y_coord(self) -> int:
        try: 
            # pos of listbox within the parent win - used to positions combo/option box
            lisbox_in_parent_coord = self.winfo_y()
            return  lisbox_in_parent_coord
        except Exception as e:
            logging.error(f"Error listbox_in_parent_y_coord: {e}", exc_info=True)
