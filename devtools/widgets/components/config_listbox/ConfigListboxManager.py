from __future__ import annotations
import logging
import tkinter as tk

from devtools.constants import ListBoxEntryInputAction, OptionBoxState
from devtools.utils import Utils
from devtools.widgets.components.config_listbox.ConfigListboxUtils import ConfigListboxUtils

"""

Inside Left window of the devtools with config settings.
Allows editing of the selected item in the listbox.
https://stackoverflow.com/a/64611569/5972531

"""
class ConfigListboxManager(tk.Listbox, ConfigListboxUtils):

    def __init__(self, 
            master, 
            update_current_selected_item_node_callback, 
            toggle_option_box_state_callback, 
            get_tree_item_callback,
            handle_subtract_callback,
            **styles
        ): 
        tk.Listbox.__init__(self, master=master, width=styles.get('width'), font=styles.get('font'))
        self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        # self.config(yscrollcommand=self.scroll_bar.set)
        self.styles = styles
        self.editting_item_index:int | None = None
        # saved callbacks
        self._handle_subtract_callback = handle_subtract_callback
        self._update_current_selected_item_node_callback = update_current_selected_item_node_callback
        self._get_tree_item_callback = get_tree_item_callback
        # listener on listbox - for editing an entry using dbl click - not used in creating init val
        self._toggle_option_box_state_callback = toggle_option_box_state_callback
        self.bind("<Double-1>", self.start_update)
        self.scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.option_box_state = OptionBoxState.CLOSED.value
        self.key_var = tk.StringVar()
        self.val_var = tk.StringVar()
        self.list_var = tk.Variable(value=[])
        self.value_box_wrapper = None
        self.key_box_wrapper = None
    # use event x and y w tk index - get listbox item index
    def _get_index_from_event_coords(self, event):
        selected_index: int = self.index(f"@{event.x},{event.y}")
        return selected_index
    
    def start_update(self, event):
        # index of clicked item on list
        updating_item_index: int = self._get_index_from_event_coords(event)
        # extract starting values from list item
        full_txt_str = self.get(updating_item_index)
    
        changes_dict  = Utils.build_split_str_pairs_dict(full_txt_str, ":")
        self.handle_entry_input_update(
            index=updating_item_index, 
            changes_dict=changes_dict,
            update_current_selected_item_node_callback=self._update_current_selected_item_node_callback
        )
        return "break"
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    def accept_edit_to_page_widget(
            self, 
            current_widget: tk.Entry | tk.OptionMenu, 
            index: int, 
            value_widget_to_destroy: tk.Widget, 
            key_widget_to_destroy: tk.Widget, 
            key_entry_value: str,
            value_entry_value: str,
            update_current_selected_item_node_callback: callable):
        # store the current y position in listbox  
        y0, _ = self.yview()       
        # delete empty entry
        is_val_widget = isinstance(value_widget_to_destroy, tk.Widget) or isinstance(value_widget_to_destroy, tk.StringVar)
        is_key_widget = isinstance(key_widget_to_destroy, tk.Widget)
        if not is_val_widget or not is_key_widget:
            fn = lambda val_type: logging.error(f"No data received for {val_type}. Cancelling edit.")
            fn("value_entry_widget") if not is_val_widget else fn("key_widget_to_destroy")

            self.delete(index)
            # after_idle runs after ant tk interals that might overwrite 
            # - move back to correct position if tk snapped it away
            self.after_idle(lambda: self.yview_moveto(y0))
            self._cancel_update(value_widget_to_destroy, key_widget_to_destroy)
            return
        # check for .get method  - use .get for new entry else val correct option box  
        value_entry_value = current_widget.get() if getattr(current_widget, 'get', None) else value_entry_value
         # delete data at current index and insert new data there
        self.delete(self.editting_item_index)
        self.insert(self.editting_item_index, Utils.build_full_input_str(key_entry_value, value_entry_value))
        
        self.after_idle(lambda: self.yview_moveto(y0))
        # send callback to update widget inside treeview
        # - options: set_tree_item_from_entry_value
        update_current_selected_item_node_callback({
            'key': key_entry_value,
            'value': value_entry_value
        })
    
        self._cancel_update(value_widget_to_destroy, key_widget_to_destroy, self.value_box_wrapper)
        return value_entry_value
     # return and place value_option_box from key_option_box
    def handle_build_value_option_box_from_key_option_box(self,index: int, key_option_box: tk.OptionMenu, value_inside: tk.StringVar, item_option_vals_list: list[str], update_current_selected_item_node_callback):
        value_option_box = self.build_value_option_box(
            index, 
            key_entry_widget=key_option_box, 
            key_entry_value=value_inside.get(),
            item_option_vals_list=item_option_vals_list, update_current_selected_item_node_callback=update_current_selected_item_node_callback)
        value_option_box.place(relx=0.3, y=self._translate_y_coord(self.editting_item_index), relwidth=0.5, width=-1)
        # value_option_box.focus_set()
        self._set_selected_by_index(index)

    def handle_build_value_entry_from_key_option_or_entry(
            self,
            index: int, 
            key_entry_widget: tk.OptionMenu | tk.Entry, 
            key_entry_value: str, 
            value_entry_value: str,
            y_coord: int,
            update_current_selected_item_node_callback,
            **kwargs):
        value_entry = tk.Entry(self, **self.styles['entry'])
        value_entry.insert(0, value_entry_value)
        value_entry.selection_from(0)
        value_entry.selection_to("end")
        value_entry.place(relx=0.3, y=y_coord, relwidth=0.58, width=-1)
        # set focus to value entry
        value_entry.focus_set()
        # set manually so curselect can access it on subract
        self._set_selected_by_index(index)
        value_entry.bind("<Return>", lambda e: self.accept_edit_to_page_widget
            (
            current_widget=e.widget, 
            index=index, 
            value_widget_to_destroy=e.widget, 
            key_widget_to_destroy=key_entry_widget,
            key_entry_value=key_entry_value,
            value_entry_value=value_entry_value,
            update_current_selected_item_node_callback=update_current_selected_item_node_callback
        ))
        
        if kwargs.get('entry_input_action') == ListBoxEntryInputAction.CREATE.value:
            value_entry.bind("<Escape>", lambda e: (self._handle_subtract_callback(e, ), self._cancel_update(e.widget, key_entry_widget)))
        else:
            value_entry.bind("<Escape>", lambda e: self._cancel_update(e.widget, key_entry_widget))
            value_entry.bind("<FocusOut>", lambda e: self._cancel_update(e.widget, key_entry_widget))
    # run funcs for entering row update - called from double click on row
    def handle_entry_input_update(
        self, 
        index: int, 
        update_current_selected_item_node_callback,
        changes_dict: dict = {}, 
    ):
        self.editting_item_index = index
        y_coord = self.bbox(index)[1]
        key_entry = tk.Entry(self, **self.styles['entry'], **self.styles['key_entry'])
        # add the text from the item into the key_entry - just place it but dont allow focus
        key_entry.insert(0, changes_dict.get('key'))
        key_entry.selection_from(0)
        key_entry.selection_to("end")
        key_entry.place(relx=0, y=y_coord, relwidth=0.5 or 1, width=-1)

        item_option_vals_list: list[str] | None = self._get_config_value_options(changes_dict.get('key'))
        if item_option_vals_list:
            value_option_box = self.build_value_option_box(
            index=index,
            key_entry_widget=key_entry,
            key_entry_value=changes_dict.get('key'),
            item_option_vals_list=item_option_vals_list,
            update_current_selected_item_node_callback=update_current_selected_item_node_callback
            )
            value_option_box.pack()
            self.value_box_wrapper.place(relx=0.3, y=self._translate_y_coord(self.editting_item_index), relwidth=0.5, width=-1)
            # value_option_box.place(relx=0.3, y=y_coord, relwidth=0.5, width=-1)
            value_option_box.focus_set()
        else:
            self.handle_build_value_entry_from_key_option_or_entry(
                index=index,
                key_entry_widget=key_entry,
                key_entry_value=changes_dict.get('key'),
                value_entry_value=changes_dict.get('value'),
                y_coord=y_coord,
                update_current_selected_item_node_callback=update_current_selected_item_node_callback
            )
    # run funcs for entering row add - called fromcalled from parent when add button clicked parent when add button clicked
    def handle_entry_input_create(
        self, 
        index: int, 
        update_current_selected_item_node_callback: callable
    ):
        item_option_vals_list = None
        # store current editting index
        self.editting_item_index = index
        # coords of y1 inside bb rect- where to place entry inside listbox
        y_coord = self.bbox(index)[1]
        current_treeview_item = self._get_tree_item_callback()
        # get possible config for values 
        current_item_options_list = current_treeview_item.config().keys()
        current_treeview_item = self._get_tree_item_callback()
        current_item_options_list = list(current_treeview_item.config().keys())
        key_option_box = self.build_key_option_box(
            index=index,
            item_option_vals_list=current_item_options_list,
            update_current_selected_item_node_callback=update_current_selected_item_node_callback
        )
        key_option_box.pack()
        self.key_box_wrapper.place(relx=0, y=self._translate_y_coord(index), relwidth=0.5, width=-1)
        key_option_box.focus_set()
        # set manually so curselect can access it on subract
        self._set_selected_by_index(index)
        