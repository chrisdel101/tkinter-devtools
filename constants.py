from enum import Enum


MAX_KEY_WIDTH = 30  # adjust as needed

KEYS_TO_REMOVE = ['class']

class ComboBoxState(Enum):
    NORMAL = "normal"
    READONLY = "readonly"