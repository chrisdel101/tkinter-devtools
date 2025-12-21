import logging
import tkinter as tk

class Store:
    """A simple store to hold key-value pairs."""
    def __init__(self):
        self.active_adding: bool = False 
        self.selected_item_tree_item: tk.Widget | None = None

    @property
    def active_adding(self):
        return self._active_adding
    
    @active_adding.setter
    def active_adding(self, value):
        logging.debug(f'SETTING ACTIVE_ADDING TO {value}')
        self._active_adding = value 
        
    @property
    def selected_item_tree_item(self):
        return self._selected_item_tree_item
    
    @selected_item_tree_item.setter
    def selected_item_tree_item(self, value):
        print('setting selected_item_tree_item to', value )
        self._selected_item_tree_item = value 