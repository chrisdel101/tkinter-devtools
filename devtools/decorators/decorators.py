
from functools import wraps
import logging
import tkinter as tk
from devtools.components.observable import Action
from devtools.constants import ActionType


def _get_observable_and_notify_(instance, message: str):
    observable = getattr(instance, '_observable', None)
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

def static_fn_try_except_catcher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except tk.TclError as e:
            logging.error(f"--tcl error in {func.__name__}: {e}---", exc_info=True)
        except Exception as e:
            logging.error(f"---ERROR in {func.__name__}: {e}---", exc_info=True)
    return wrapper

def class_fn_try_except_catcher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # will be the class that is decorated
        caller_instance = args[0] if args else None
        try:
            return func(*args, **kwargs)
        except tk.TclError as e:
            logging.error(f"--tcl error in {func.__name__}: {e}---", exc_info=True)
            if caller_instance:
                _get_observable_and_notify_(caller_instance, str(e))
        except Exception as e:
            logging.error(f"---ERROR in {func.__name__}: {e}---", exc_info=True)
    return wrapper
