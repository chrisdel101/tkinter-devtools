import logging
import tkinter as tk

class Store:
    """A simple store to hold key-value pairs."""
    def __init__(self):
        self.active_adding: bool = False 
        self.selected_item_tree_item: tk.Widget | None = None
        self.selected_combobox_wrapper: tk.Widget | None = None
        self.selected_combobox: tk.Widget | None = None
        self.devtools_window_in_focus: bool = True
        self.combobox_popdown_open: bool = False
        self.editting_item_index:int | None = None      

    @property
    def editting_item_index(self):
        return self._editting_item_index
    
    @editting_item_index.setter
    def editting_item_index(self, value):
        self._editting_item_index = value 

    @property
    def combobox_popdown_open(self):
        return self._combobox_popdown_open
    
    @combobox_popdown_open.setter
    def combobox_popdown_open(self, value):
        self._combobox_popdown_open = value 

    @property
    def selected_combobox_wrapper(self):
        return self._selected_combobox_wrapper
    
    @selected_combobox_wrapper.setter
    def selected_combobox_wrapper(self, value):
        self._selected_combobox_wrapper = value 

    @property
    def active_adding(self):
        return self._active_adding
    
    @active_adding.setter
    def active_adding(self, value):
        # logging.debug(f'SETTING ACTIVE_ADDING TO {value}')
        self._active_adding = value 
        
    @property
    def selected_item_tree_item(self):
        return self._selected_item_tree_item
    
    @selected_item_tree_item.setter
    def selected_item_tree_item(self, value):
        # print('setting selected_item_tree_item to', value )
        self._selected_item_tree_item = value 

    # remove any selected comboboxs or wrappers in state
    def focus_out_untrack_comboboxs_or_wrappers(self):
        if self.selected_combobox_wrapper:
            logging.debug(f"Combobox removed from state.")
            self.selected_combobox_wrapper = None

    # track frame and inner combobox - when window focus out - cancel all comboboxes - called in build_key_option_box
    def track_any_selected_combobox_or_wrapper(self,widget):
    # - combobox widget cannot focusout itself
        try:
            if widget.winfo_name() == "!combobox":
                # store combobox i
                logging.debug(f"Combobox selected1 NO LOGIC: {widget.get()}")
            else:    
                for child in widget.winfo_children():
                    if child.winfo_name() == "!combobox":
                        # store wrapper if child is combobox
                        self.selected_combobox_wrapper = widget
                        self.selected_combobox = child
                        logging.debug(f"Combobox added to state.")
                        # logging.debug(f"Combobox state added: {widget}")
                        break
              
        except Exception as e:
            logging.error(f"Error tracking combobox selection: {e}", exc_info=True)

