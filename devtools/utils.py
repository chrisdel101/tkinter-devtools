from __future__ import annotations
import logging

from devtools.widgets.components.ConfigListboxManager import OPTIONS
from devtools.constants import CommonConfigAttr



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
    def remove_junk_config_items(config):
        try:
            common_attributes = [e.value for e in CommonConfigAttr]
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
    # find keys with valid values {'width':10}
    def extract_actual_config_values(config):
        try:
            key_val_config = {}
            for key, val in config.items():
                if isinstance(val, tuple):
                    # extract all values that do not match the key - if key are the same as values
                    non_key_matches = [item for item in val if (isinstance(item, str) and (item or "").lower()) != (key or "").lower()]

                    for non_key_match in non_key_matches:
                       if (option := OPTIONS.get(key)):
                           type_allowed = option.get('type')
                           if (type(non_key_match).__name__ or "").lower() == type_allowed:
                               key_val_config[key] = non_key_match
                if isinstance(val, (str, int, float)):
                    if OPTIONS.get(val):
                        key_val_config[key] = val
            return key_val_config
        except Exception as e:
            logging.error(f"Error extracting actual config values: {e}", exc_info=True)
            raise e     