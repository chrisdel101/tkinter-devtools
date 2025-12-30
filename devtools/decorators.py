
from functools import wraps
import logging

# focus out guard - if true block any logic that runs on key_combo_box focus out - listbox_key_focus_out
# mostly to handle focusset from key-value option
def toggle_block_focus_out_key_logic(func):
    try:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            finally:
                self._store.allow_input_focus_out_logic = False
                    
        return wrapper
    except Exception as e:
        logging.error("Error in toggle_block_focus_out_key_logic decorator.", exc_info=True)