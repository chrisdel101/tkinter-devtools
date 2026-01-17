
from functools import wraps
import logging
import tkinter as tk

# focus out guard - if true block any logic that runs on key_combo_box focus out - listbox_key_focus_out
# mostly to handle focusset from key-value option
def block_allow_input_focus_out_logic(func):
    try:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            finally:
                self._store.allow_input_focus_out_logic = False
                    
        return wrapper
    except Exception as e:
        logging.error("Error in block_allow_input_focus_out_logic decorator.", exc_info=True)

def try_except_catcher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except tk.TclError as e:
            logging.error(f"--SAFE_CONFIG ERROR--- in {func.__name__}: error {e}---", exc_info=True)
            raise e
        except Exception as e:
            logging.error(f"---ERROR in {func.__name__}: {e}---", exc_info=True)
    return wrapper