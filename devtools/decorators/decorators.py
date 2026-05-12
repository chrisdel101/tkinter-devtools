
from functools import wraps
import logging
import tkinter as tk
from devtools.components.observable import Action
from devtools.constants import ActionType

def _notify_error(self, message: str):
    observable = getattr(self, '_observable', None)
    if observable:
        observable.notify_observers(Action(type=ActionType.SHOW_RIGHT_WINDOW_ERROR, data=message))

# focus out guard - if true block any logic that runs on key_combo_box focus out - listbox_key_focus_out
# mostly to handle focusset when adding key-value boxes - and doing focusset
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
            logging.error(f"--tcl error in decorator --- in {func.__name__}: error {e}---", exc_info=True)
            _notify_error(args[0] if args else None, str(e))
        except Exception as e:
            logging.error(f"---ERROR in {func.__name__}: {e}---", exc_info=True)
    return wrapper