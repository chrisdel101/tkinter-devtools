
from typing import Any

# state context is an observer pattern - this is the Subect
class SubjectState:
    def __init__(self) -> None:
        self._observers = []

    def register_observer(self, observer) -> None:
        self._observers.append(observer)

    def notify_observers(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        for observer in self._observers:
            observer.notify(self, *args, **kwargs)
   