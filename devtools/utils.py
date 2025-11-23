from __future__ import annotations
import logging

from devtools.constants import KEYS_TO_REMOVE


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
    def config_listbox_value_filter_helper(value):
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
    def filter_config_values(config):
            filtered = {}
            for key, values in config.items():
                # The "actual value" may be the last element? Or you pick which?
                # From your example, the last element seems to be the current value
                current_value = values[-1]
                if key in KEYS_TO_REMOVE:
                    continue
                if Utils.config_listbox_value_filter_helper(current_value):
                    filtered[key] = current_value
            return filtered