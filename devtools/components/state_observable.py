
from typing import Any

# this is the Subject
class StateObservable:
    def __init__(self) -> None:
        self._observers = []
        self.active_adding: bool = False 

    @property
    def active_adding(self):
        return self._active_adding
    
    @active_adding.setter
    def active_adding(self, value):
        print('setting active_adding to', value )
        self._active_adding = value 

    def register_observer(self, observer) -> None:
        self._observers.append(observer)

    def notify_observers(self, **kwargs: dict[str, Any]) -> None:
        for observer in self._observers:
            observer.notify(self, **kwargs)
   