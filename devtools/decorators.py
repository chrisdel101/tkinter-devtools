
from functools import wraps
import logging


def toggle_key_option_focus(func):
    try:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self._key_option_focus_change = False
            try:
                return func(self, *args, **kwargs)
            finally:
                self._key_option_focus_change = False
                    
        return wrapper
    except Exception as e:
        logging.error("Error in toggle_key_option_focus decorator.", exc_info=True)