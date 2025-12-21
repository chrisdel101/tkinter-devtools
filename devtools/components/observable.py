
from typing import Any
import tkinter as tk

# this is the Subject
class Observable:
    def __init__(self) -> None:
        self._observers = []

    def register_observer(self, observer) -> None:
        self._observers.append(observer)

    def notify_observers(self, **kwargs: dict[str, Any]) -> None:
        for observer in self._observers:
            observer.notify(**kwargs)
   