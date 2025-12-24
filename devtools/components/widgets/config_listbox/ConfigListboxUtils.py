import logging
import tkinter as tk
from tkinter import ttk

from devtools.components.observable import Action
from devtools.constants import ActionType, ListBoxEntryInputAction, OptionBoxState
from devtools.maps import CONFIG_SETTING_VALUES
from devtools.utils import Utils

class ConfigListboxUtils:

    def build_value_option_box(self, 
        index: int,
        key_entry_widget: tk.Entry | tk.OptionMenu,
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
        value_option_box = tk.OptionMenu(self.value_box_wrapper,
            value_inside,
            *self.list_var.get(),
            )
        # on option_box value select
        value_inside.trace_add('write', lambda *args:self.insert_value_output_and_apply_to_page
            (current_widget=value_option_box, 
             index=index,
             value_widget_to_destroy=value_option_box, 
             key_widget_to_destroy=key_entry_widget,
             key_entry_value=key_entry_value,
             value_entry_value=value_inside.get(), 
        ))
       
        value_option_box.bind("<Escape>", lambda e: (
            self._cancel_update(value_option_box, key_entry_widget, self.key_box_wrapper, self.value_box_wrapper), 
            self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT.name)), 
            setattr(self._store, 'active_adding', False)))
        # get menu btn par ent - only way to detect bind 
        btn = value_option_box.children['menu'].master
        btn.bind("<FocusOut>", lambda e: ((
            self._cancel_update(value_option_box, key_entry_widget, self.key_box_wrapper, self.value_box_wrapper)), 
            self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT.name)), 
            print("focus out build_value_option_box")), 
            setattr(self._store, 'active_adding', False))

        return value_option_box
        

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
            # on selectd select - build and pack value option box if list values
            key_combo_box.bind("<<ComboboxSelected>>", lambda e: 
                self.handle_build_value_option_box_from_key_option_box( index=index,
                key_option_box=key_combo_box,
                value_inside=value_inside,
                item_option_vals_list=self._get_config_value_options(value_inside.get()),
                ) if self._get_config_value_options(value_inside.get()) else 
                self.handle_build_value_entry_from_key_option_or_entry(
                index=index,
                key_entry_widget=key_combo_box,
                key_entry_value=value_inside.get(),
                value_entry_value="",
                y_coord=self.bbox(self._store.editting_item_index)[1],
                **{'entry_input_action':ListBoxEntryInputAction.CREATE.value})
                )
            # this is when adding new line with new key item entry - subtract list item and cancel option box
            key_combo_box.bind("<Escape>", lambda e: 
                (self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT.name)), 
                 self._cancel_update(key_combo_box, self.key_box_wrapper), 
                 setattr(self._store, 'active_adding', False))) 
            # use native tcl to detect when open
            key_combo_box.bind("<Button-1>", self._handle_combobox_open)
            # exists when open
            popdown = self.tk.call("ttk::combobox::PopdownWindow", key_combo_box)
            # unmap fires when widget is removed or hidden
            self.tk.call(
                "bind",
                popdown,
                "<Unmap>",
                self.register(self._handle_combobox_closed)
            )
            key_combo_box.bind("<FocusOut>", lambda e: 
                self._on_focus_out(e, key_combo_box, self.key_box_wrapper))
            self._store.track_any_selected_combobox_or_wrapper(self.key_box_wrapper)
            return key_combo_box
        except Exception as e:
            logging.error("Error building key option box.", exc_info=True)
    # if open flip state to closed - called on tcl unmap
    def _handle_combobox_closed(self):
        try:
            if self._store.combobox_popdown_open:
                self._store.combobox_popdown_open = False
                logging.debug(f"Combobox popdown closed state: {self._store.combobox_popdown_open}")
        except Exception as e:
            logging.error(f"Error _handle_combobox_closed: {e}", exc_info=True)
    # when arrow clicked flip to open
    def _handle_combobox_open(self, e):
        try:
            check = Utils.is_combobox_arrow(e.widget, e.x)
            if check:
                if not self._store.combobox_popdown_open:
                    self._store.combobox_popdown_open = True
                logging.debug(f"_handle_combobox_open open state: {self._store.combobox_popdown_open}")
        except Exception as e:
            logging.error(f"Error _handle_combobox_open: {e}", exc_info=True)

    def _on_focus_out(self,e, *args):
        if not self._key_option_focus_change:
            return  # internal focus change → ignore
        if self._store.combobox_popdown_open: 
            return
        logging.debug("_on_focus_out build_key_option_box")
        self._store.active_adding =  False
        self._observable.notify_observers(Action(type=ActionType.HANDLE_SUBTRACT.name))
        self._cancel_update(*args)
    # get options of config properties to use in dropdown - if they exist
    @staticmethod
    def _get_config_value_options(key_str_value:str=None) -> list| str:
        if not key_str_value:
            return 
        # check for options in map
        options_list = (CONFIG_SETTING_VALUES.get(key_str_value) or {}).get('values')
        if options_list is None:
            logging.debug(f"_get_config_value_options: {key_str_value} not mapped. Either it's not a list value or it was missed in Utils.filter_non_used_config_attrs.", exc_info=True)
        return options_list
    
    @staticmethod
    def _cancel_update(widget, *args):
        widget.destroy()
        for arg in filter(None, args):
            arg.destroy()
    
    def _delete(self):
        self.delete(0, tk.END)
    # on init - load selected tree items attrs into listbox
    # runs from treeview
    def _insert_all(self, config_dict):
         for key in config_dict:
            # insert selected node into styles_window_listbox window
            display = f"{key}: {config_dict[key]}"
            # this auto sizes w/o adding styles
            self.insert(tk.END, display)

    # UNUSED - set to open on click - only handles open since close is not detectable
    def set_box_state_on_open(self, event):
        # if open set to closed - else set to open
        if self.option_box_state == OptionBoxState.CLOSED.value:
            self.option_box_state = OptionBoxState.OPEN.value
            # logging.debug("Option box opened.")
        else:
            self.option_box_state = OptionBoxState.CLOSED.value
            # logging.debug("Option box closed.")

    def _set_selected_by_index(self, index:int):
        # clear other selections
        self.selection_clear(0, "end")
        # select row
        self.selection_set(index)
        # activate on keyboard
        self.activate(index)

    # frame wrapper causes an offset of the optionboxes - adjusting w the parent y coord 
    def _translate_y_coord(self, index:int) -> int:
        widget_in_listbox_coord = self.bbox(index)[1]
        lisbox_in_parent_coord = self.winfo_y()
        return widget_in_listbox_coord + lisbox_in_parent_coord
