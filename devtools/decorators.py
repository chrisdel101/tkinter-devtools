
from functools import wraps
import logging

# block key box focusout cancel - only allow key focus for functions called
#  - used to stop focus when focusset is called after key box moves to value box
def toggle_key_option_focus(func):
    try:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self._key_option_focus_change = True
            try:
                logging.debug(f"decorator focus locked: {self._key_option_focus_change}")
                return func(self, *args, **kwargs)
            finally:
                self._key_option_focus_change = False
                logging.debug(f"decorator focus locked: {self._key_option_focus_change}")
                    
        return wrapper
    except Exception as e:
        logging.error("Error in toggle_key_option_focus decorator.", exc_info=True)