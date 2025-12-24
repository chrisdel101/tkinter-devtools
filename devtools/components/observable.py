
from typing import Any
import tkinter as tk
from dataclasses import dataclass

from devtools.constants import ActionType

@dataclass(frozen=True)
class Action:
    type: ActionType
    data: Any | None = None

# this is the Subject
class Observable:
    def __init__(self) -> None:
        self._observers = []

    def register_observer(self, observer) -> None:
        self._observers.append(observer)

    def notify_observers(self, action: Action) -> None:
        for observer in self._observers:
            observer.notify(action)