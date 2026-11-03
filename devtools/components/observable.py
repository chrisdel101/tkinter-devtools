
from typing import Any
from dataclasses import dataclass

from devtools.constants import ActionType

@dataclass(frozen=True)
class Action:
    type: ActionType
    # payload passed to the handler method as args/kwargs
    data: Any | None = None
    # optional widget instance to restrict delivery — when set, only the observer
    # whose identity matches target will handle the action; all others skip it.
    # when None, every observer that has a matching handler will run.
    target: Any | None = None

# this is used in place of having to pass callbacks up and down everywhere
class Observable:
    def __init__(self) -> None:
        self._observers = []

    def register_observer(self, observer) -> None:
        self._observers.append(observer)

    # returns each observer's result so the caller can tell if the update worked
    def notify_observers(self, action: Action) -> list:
        return [observer.notify(action) for observer in self._observers]