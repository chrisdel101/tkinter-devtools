from __future__ import annotations
import logging
from tkinter import ttk

from devtools.components.observable import Action
from devtools.constants import COMBOBOX_ARROW_OFFSET, ValidConfigAttr
from devtools.maps import ACTION_REGISTRY, CONFIG_SETTING_VALUES, CONFIG_ALIASES

class Utils:
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
    def build_split_str_pairs_dict(new_data, separator=":"):
        try:
            # split list into sep str
            split_list_items: list = new_data.split(separator)
            key = split_list_items[0] if len(split_list_items) > 0 else ""
            value = split_list_items[1] if len(split_list_items) > 1 else ""
            changes_dict  = {
                'key': key,
                'value': (value or "").strip(),
            }
            return changes_dict
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
    # remove any non standard unusable attrs like screen, use
    def filter_non_used_config_attrs(config):
        try:
            common_attributes = [e.value for e in ValidConfigAttr]
            # value can be tuple or str/int
            for key in list(config.keys()):
            # delete unwanted config values from dict in place using list
                if key not in common_attributes:
                    del config[key]
            return config
        except Exception as e:
            logging.error(f"Error removing junk config items: {e}", exc_info=True)
            raise e
    @staticmethod
    # check for tuple length. if 5 it's last item, if 2 it's an alias
    # This is a tk inter standard for all configs objs
    def extract_current_config_key_values(config):
        try:
            key_val_dict = {}
            # use names from enum values
            valid_names = {e.value for e in ValidConfigAttr}
            for key, val in config.items():
                # resolve alias to full name - or just return name ie borderwidth
                canonical = Utils.config_attr_resolver(key)
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
    @staticmethod
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
                        if (setting_value := CONFIG_SETTING_VALUES.get(key)):
                            type_allowed = setting_value.get('type')
                        # check if current setting matches a type that's allowed
                            if ((type(difference).__name__ or "").lower() == type_allowed and difference) != "":
                                if key_val_config.get(key) == None:
                                    key_val_config[key] = difference
                elif isinstance(val, (str, int, float)):
                    if CONFIG_SETTING_VALUES.get(key):
                        key_val_config[key] = val
            return key_val_config
        except Exception as e:
            logging.error(f"Error extracting actual config values: {e}", exc_info=True)
            raise e 
          
    @staticmethod 
    # resolve aliases to call matching value          
    def config_attr_resolver(attr_str: str):
    # check if it's alias mapping to a full config attr - else return as is
        resolved = CONFIG_ALIASES.get(attr_str, attr_str)
        return resolved
    # using focus_displayof causes combobox KeyError: 'popdown'
    @staticmethod
    def _safe_focus_displayof(widget):
        try:
            return widget.focus_displayof()
        except KeyError:
            # ttk Combobox popdown (not in widget tree)
            return widget
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
    # universal fn called in class notify methods
    def dispatch_action(self, action: Action):
        # check if action maps to a method on this class
        fn = getattr(self, ACTION_REGISTRY.get(action.type), None)
        if fn:
            if isinstance(action.data, (list, tuple)):
                fn(*action.data)
            else:
                fn(action.data)
            
        
