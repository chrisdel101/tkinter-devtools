from enum import Enum


MAX_KEY_WIDTH = 30  # adjust as needed

KEYS_TO_REMOVE = ['class']

class ComboBoxState(Enum):
    NORMAL = "normal"
    READONLY = "readonly"

class OptionBoxState(Enum):
    OPEN = "open"
    CLOSED = "closed"
# create used when adding and no val is being input
class ListBoxEntryInputAction(Enum):
    CREATE = "create"
    UPDATE = "update"