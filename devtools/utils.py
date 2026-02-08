from __future__ import annotations
from ast import Store
from copy import copy
import logging
import tkinter as tk
from tkinter import ttk

from devtools.components.observable import Action
from devtools.constants import COMBOBOX_ARROW_OFFSET, GeometryType, ConfigOptionName, CommonGeometryOption, GridGeometryOption, GridGeometryOption, ListboxItemPair, PackGeometryOptionName, PlaceGeometryOption
from devtools.decorators import try_except_catcher
from devtools.geometry_info import GeometryManagerInfo
from devtools.maps import ACTION_REGISTRY, CONFIG_OPTION_SETTINGS, CONFIG_ALIASES

class Utils:
    @staticmethod
    # Check false but excluding zero
    def non_zero_falsey(value) -> bool:
        # true for None and ""
        if not isinstance(value, (int, float)) and not value:
            return True
        return False
    @staticmethod
    # loops over widget config options and applies any matches - skips invalid options
    def match_safe_kwargs(widget_cls, master, **kwargs):
        '''
        @param widget_cls: The Tkinter widget class (e.g., tk.Button, tk.Label), not instance.
        @param master: The parent widget.
        @param kwargs: The keyword arguments to filter and apply - mainly a Styles dict.
        '''
        valid = widget_cls(master).keys()  # valid Tk options
        return {k: v for k, v in kwargs.items() if k in valid}

    @staticmethod
    # split a key value str and return key/val dict
    def build_split_str_pairs_dict(new_data: str, separator: str = ":") -> ListboxItemPair:
        try:
            # split list into sep str
            split_list_items: list = new_data.split(separator)
            key = split_list_items[0] if len(split_list_items) > 0 else ""
            value = split_list_items[1] if len(split_list_items) > 1 else ""
            listbox_item_pairs_dict  = {
                'key': key,
                'value': (value or "").strip(),
            }
            return listbox_item_pairs_dict
        except Exception as e:
            logging.error(f"Error splitting string at colon: {e}", exc_info=True)
            raise e
    @staticmethod
    # split a key value str and return key/val dict
    def build_full_input_str(key_str, value_str):
        try:
            full_str = f"{key_str}: {value_str}"
            return full_str
        except Exception as e:
            logging.error(f"Error build_full_input_str string at colon: {e}", exc_info=True)
            raise e
    # filter out unwanted values from widget.config
    @staticmethod
    def config_value_stripper(value):
        # Convert to string for simple checks
        val_str = str(value).strip().lower()

        # Skip empty or zero-like values
        if val_str in ('', '0', 'none', 'false'):
            return False

        # Skip values starting with dash (like '-borderwidth', '-background')
        if val_str.startswith('-'):
            return False
    
        # Skip system placeholders or common "default" words (case-insensitive)
        system_defaults = [
            'systemwindowbackgroundcolor',
            'systemtextcolor',
            'systemhighlightcolor',
            'systemhighlightbackground',
            'systembuttonface',
            'systembuttontext',
            'systemwindowtext',
            'systembuttonshadow',
            'systempressedbuttontextcolor',
            'tkdefaultfont'
        ]
        if val_str in system_defaults:
            return False

        return True
    @staticmethod
    # remove any non standard unusable options like screen, use
    def filter_non_used_config_options(config):
        try:
            common_options = [e.value for e in ConfigOptionName]
            # value can be tuple or str/int
            for key in list(config.keys()):
            # delete unwanted config values from dict in place using list
                if key not in common_options:
                    del config[key]
            return config
        except Exception as e:
            logging.error(f"Error removing junk config items: {e}", exc_info=True)
            raise e
    @staticmethod
    @try_except_catcher
    # remove any non standard unusable options
    def build_geometry_standard_options_dict(geo_manager: GeometryManagerInfo):
        # get all common option keys for geo type
        match geo_manager.geometry_type:
            case GeometryType.PACK:
                common_options  = [getattr(PackGeometryOptionName, k) for k in filter(str.isupper, dir(PackGeometryOptionName))]
            case GeometryType.GRID:
                common_options = [getattr(GridGeometryOption, k) for k in filter(str.isupper, dir(GridGeometryOption))]
            case GeometryType.PLACE:
                common_options = [getattr(PlaceGeometryOption, k) for k in filter(str.isupper, dir(PlaceGeometryOption))]
        # geo_manager.geometry_options ex - {'in': <tkinter.Tk object .>, 'anchor': 'center', 'expand': 0,...} 
        for key, val in list(geo_manager.geometry_options.items()):
        # delete unwanted config values in place using tuples list
            if Utils.non_zero_falsey(val):
                del geo_manager.geometry_options[key]
            elif key not in common_options:
                del geo_manager.geometry_options[key]
        return geo_manager.geometry_options

    @staticmethod
    # check for each tuple length. if 5 it's last item, if 2 it's an alias
    # This is a tk inter standard for all configs objs
    def conform_option_lisbox_config(config):
        try:
            key_val_dict = {}
            # use names from enum values
            valid_names = {e.value for e in ConfigOptionName}
            for key, val in config.items():
                # resolve alias to full name - or just return name ie borderwidth
                canonical = Utils.listbox_option_alias_resolver(key)
                # check that name is part is one if valid ones - stop if not
                if canonical not in valid_names:
                    continue             
                # in 5 len tuple we want last item for value
                config_named_lookup: tuple | str | int = config.get(canonical)
                if isinstance(config_named_lookup, tuple):
                    if len(config_named_lookup) == 5:
                        # last item is always val - in 5 len tuple
                        actual_value = config_named_lookup[-1]
                        # if not already added and value is not empty str
                        if key_val_dict.get(key) == None and actual_value != "":
                            key_val_dict[canonical] = actual_value
                    else: 
                        # if not 5 len tuple break error
                        err_msg = f"get_valid_key_value_differences: tuple is len {len(config_named_lookup)}, not len 5. Invalid len"
                        logging.error(err_msg)
                        raise ValueError(err_msg)
                elif isinstance(val, (str, int, float)):
                    # if not already added and value is not empty str
                    if key_val_dict.get(key) == None and config_named_lookup != "":
                        # it's just a single key value pair
                        key_val_dict[canonical] = config_named_lookup

            return key_val_dict
        except Exception as e:
            logging.error(f"Error extracting actual config values: {e}", exc_info=True)
            raise e 
        
    @staticmethod
    def merge_dicts(*dicts) -> dict:
        try:
            merged = {}
            for d in dicts:
                # dict union operator, like .update
                merged |= d 
            return merged
        except Exception as e:
                logging.error(f"Error merge_dicts: {e}", exc_info=True)
                raise e
    @staticmethod
    def sorted_dict(unsorted_dict: dict) -> dict:
        try:
            d = dict(sorted(unsorted_dict.items()))
            return d
        except Exception as e:
            logging.error(f"Error sorting_dict: {e}", exc_info=True)
            raise e
    @staticmethod # NOT USED
    # compare L1 - L2 return the differences - check if a difference is valid as a setting value
    def get_valid_key_value_differences(config):
        try:
            key_val_config = {}
            for key, val in config.items():
                if isinstance(val, tuple):
                    # many values must mirror the keys - find difference
                    differences = [item for item in val if (isinstance(item, str) and (item or "").lower()) != (key or "").lower()]
                    # for each difference check if it an an actual setting value - we want these
                    for difference in differences:
                        if (setting_value := CONFIG_OPTION_SETTINGS.get(key)):
                            type_allowed = setting_value.get('type')
                        # check if current setting matches a type that's allowed
                            if ((type(difference).__name__ or "").lower() == type_allowed and difference) != "":
                                if key_val_config.get(key) == None:
                                    key_val_config[key] = difference
                elif isinstance(val, (str, int, float)):
                    if CONFIG_OPTION_SETTINGS.get(key):
                        key_val_config[key] = val
            return key_val_config
        except Exception as e:
            logging.error(f"Error extracting actual config values: {e}", exc_info=True)
            raise e 
          
    @staticmethod 
    # resolve aliases to call matching value          
    def listbox_option_alias_resolver(option: str):
    # check if it's alias mapping to a full config option - else return as is
        resolved = CONFIG_ALIASES.get(option, option)
        return resolved
    # using focus_displayof causes combobox KeyError: 'popdown'
    @staticmethod
    def _safe_focus_displayof(widget):
        try:
            return widget.focus_displayof()
        except KeyError:
            # ttk Combobox popdown (not in widget tree)
            return widget
    # check if current cursor click is the arrow area of the combobox
    @staticmethod
    def is_combobox_arrow(combobox: ttk.Combobox, x: int) -> bool:
        try:
           combobox_arrow_area = combobox.winfo_width() - COMBOBOX_ARROW_OFFSET
           if x >= combobox_arrow_area:
                return True
           return
        except Exception:
            logging.error("Error determining if click was on combobox arrow.", exc_info=True)
    @staticmethod
    @try_except_catcher
    # universal fn called in class notify methods
    def dispatch_action(self, action: Action):
            # check any targets match the current obj - for multi instance
            if action.target is not None and action.target is not self:
                logging.low_trace(f"Target set to {action.target.name}. Ignoring mismatch to {self}.")
                return
            # check if action maps to a method on this class
            fn = getattr(self, ACTION_REGISTRY.get(action.type.name), None)
            if fn:
                if isinstance(action.data, (list, tuple)):
                    fn(*action.data)
                elif isinstance(action.data, (dict)):
                    fn(**action.data)
                else:
                    # don't input anything if no data
                    fn(action.data) if action.data is not None else fn()
    @staticmethod    
    @try_except_catcher
    def check_widget_geometry_manager_info(widget: tk.Widget):
        geometry_type = widget.winfo_manager()
        match geometry_type:
            case GeometryType.PACK.value:
                return GeometryManagerInfo(GeometryType.PACK, widget.pack_info(), name=widget.winfo_name())
            case GeometryType.GRID.value:
                return GeometryManagerInfo(GeometryType.GRID, widget.grid_info(), name=widget.winfo_name())
            case GeometryType.PLACE.value:       
                return GeometryManagerInfo(GeometryType.PLACE, widget.place_info(), name=widget.winfo_name())
            case GeometryType.BLANK.value:
                logging.trace(f"check_widget_geometry_manager_info: Widget {widget} is not mapped.")
                return GeometryManagerInfo(GeometryType.BLANK, {} , name=widget.winfo_name())
            case GeometryType.WM.value:
                logging.trace(f"check_widget_geometry_manager_info: Widget {widget} uses wm - rejected.")
                return None
            case _:
                logging.warning(f"check_widget_geometry_manager_info: Widget {widget} has no geometry manager.")
                return None
            
    @staticmethod
    def _track_hidden_widgets(widget, store, geo_manager_info: GeometryManagerInfo):
        # combine new widgets with any stored ones
        hidden_widgets = Utils.merge_dicts(store.hidden_widgets or {}, {id(widget): geo_manager_info})
        store.hidden_widgets = hidden_widgets

    @staticmethod
    def _untrack_hidden_widgets(updated_hidden_widgets, store):
        # overwrite with updated copy
        store.hidden_widgets = updated_hidden_widgets
    
    @staticmethod
    def hide_widget(widget: tk.Widget, store: Store):
        # check if already hidden - do nothing
        is_widget_hidden = store.hidden_widgets.get(id(widget))
        if is_widget_hidden:
            return
        geo_manager_info = Utils.check_widget_geometry_manager_info(widget)
        # store state of hidden widget to restore later
        Utils._track_hidden_widgets(widget, store, geo_manager_info)
        if geo_manager_info is None:
            return
        match geo_manager_info.geometry_type:
            case GeometryType.PACK:
                widget.pack_forget()
            case GeometryType.GRID:
                widget.grid_forget()
            case GeometryType.PLACE:
                widget.place_forget()
        

    @staticmethod
    # show an unmapped widget
    def show_widget(widget: tk.Widget, store: Store, geometry_type: GeometryType | None = None):
        # if no state store will be no options set
        widget_state = store.hidden_widgets.get(id(widget))
        # if not stored state need to manually set i.e. from page
        geo_type  = widget_state.geometry_type if widget_state else geometry_type
        if not geo_type:
            logging.trace(f"show_widget: Widget {widget} has no stored hidden state.")
            return
        match geo_type:
            case GeometryType.PACK:
                widget.pack(**widget_state.geometry_options)
            case GeometryType.GRID:
                widget.grid(**widget_state.geometry_options)
            case GeometryType.PLACE:
                widget.place(**widget_state.geometry_options)
            case _:
                logging.warning(f"show_widget: Widget {widget} has unknown geometry type {geo_type}.")
                return
        # make shallow copy 
        hidden_widgets_copy = copy(store.hidden_widgets)
        #  remove showed widgets from hidden_widgets copy - it's vibile now
        del hidden_widgets_copy[id(widget)]
        # overwrite hidden state with the copy
        Utils._untrack_hidden_widgets(hidden_widgets_copy, store)

    @staticmethod
    @try_except_catcher
    # combine any extra missing options here
    def combine_additional_geometry_ooptions(widget) -> dict:
        # get geo manager and value
        geo_manager: GeometryManagerInfo = Utils.check_widget_geometry_manager_info(widget)
        resolved_combined_widget_geometry ={}
        if geo_manager:
            options_key_value_dict = Utils.build_geometry_standard_options_dict(geo_manager)
            combined_widget_geometry = Utils.merge_dicts(
                {
                    # ADD EXTRA OPTIONS HERE IF NEEDED
                    CommonGeometryOption.GEOMETRY_TYPE: geo_manager.geometry_type
                }, 
                options_key_value_dict
            )
            return combined_widget_geometry
        return {}
    @staticmethod
    @try_except_catcher
    def resolve_geometry_aliases(combined_widget_geometry: dict) -> dict:
        new_combined_widget_geometry = {}
        for key, val in combined_widget_geometry.items():
                # resolve alias or keep key as is
                canonical = Utils.listbox_option_alias_resolver(key)
                new_combined_widget_geometry[canonical] = val
             
        return new_combined_widget_geometry   
    @staticmethod
    # handle invalid values passed to config
    def safe_config(widget, **kwargs):
        prev = {}
        # store state of current var
        for k in kwargs:
            prev[k] = widget.cget(k)
        try:
            # try value on config - no error means success
            widget.config(**kwargs)
        # hits this when bad config value is added 
        except tk.TclError as e:
            logging.debug(f"---SAFE_CONFIG ERROR---: Invalid input: {kwargs}: error: {e}")
            # raise to next catch block - error chain should stop it making it to page
            raise e
        except Exception as e:
            logging.error(f"safe_config: Error configuring {widget}: {e}", exc_info=True)
            raise e
