import logging
import tkinter as tk

from constants import ListBoxEntryInputAction, OptionBoxState
from maps import OPTIONS
from utils import Utils

"""

Inside Left window of the devtools with config settings.
Allows editing of the selected item in the listbox.
https://stackoverflow.com/a/64611569/5972531

"""
class ConfigListboxManager(tk.Listbox):

    def __init__(self, 
            master, update_current_selected_item_node_callback, 
            toggle_option_box_state_callback, 
            get_tree_item_callback,
            **styles
        ): 
        self.scroll_bar = tk.Scrollbar(master, orient="vertical", command=self.yview)
        tk.Listbox.__init__(self, master=master, width=styles.get('width'),  yscrollcommand = self.scroll_bar.set, font=styles.get('font'))
        self.styles = styles
        self.editting_item_index:int | None = None
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
          
       
    # use event x and y w tk index - get listbox item index
    def _get_index_from_event_coords(self, event):
        selected_index: int = self.index(f"@{event.x},{event.y}")
        return selected_index
    
    def start_update(self, event):
        # index of clicked item on list
        updating_item_index: int = self._get_index_from_event_coords(event)
        
        full_txt_str = self.get(updating_item_index)
        # when val is blank it's using add btn
        entry_input_action: ListBoxEntryInputAction = ListBoxEntryInputAction.CREATE.value if full_txt_str == "" else ListBoxEntryInputAction.UPDATE.value

        changes_dict  = Utils.build_split_str_pairs_dict(full_txt_str, ":")
        self.handle_create_entry_input(
            index=updating_item_index, 
            changes_dict=changes_dict,
            entry_input_action=entry_input_action,
            update_current_selected_item_node_callback=self._update_current_selected_item_node_callback
        )
        return "break"
    def _on_return_create(self, e):
                # get key val asign to var
                self.key_var.set(e.widget.get())
                if not self.key_var.get():
                    return
                item_mapped_list: list[str] | None = self._get_config_value_options(self.key_var.get())
                if item_mapped_list:
                    option_box = self._handle_value_option_box(
                    index=self.editting_item_index,
                    y_coord=self.bbox(self.editting_item_index)[1],
                    key_entry=e.widget,
                    item_mapped_list=item_mapped_list,
                    update_current_selected_item_node_callback=self._update_current_selected_item_node_callback
                    )
                    option_box.place(relx=0.3, y=self.bbox(self.editting_item_index)[1], relwidth=0.5, width=-1)
                    option_box.focus_set()

    # update listbox item
    # - fires on clicks
    # - as  single entry or dropdown for edits
    # - as  two sep entries for adding new
    def handle_create_entry_input(
        self, 
        index: int, 
        entry_input_action: ListBoxEntryInputAction,
        update_current_selected_item_node_callback,
        changes_dict: dict = {}, 
        current_treeview_widget: tk.Widget = None
    ):
        item_mapped_list = None
        # store current editting index
        self.editting_item_index = index
        # coords of y1 inside bb rect- where to place entry inside listbox
        y_coord = self.bbox(index)[1]
        # --- KEY ENTRY ---
        # add an entry box on top of listbox item
        # trace_add write fires on select 
        # key_entry = tk.Entry(self, **self.styles['entry'], textvariable=self.key_var, **self.styles['key_entry'])
        # key_entry.selection_from(0)
        # key_entry.selection_to("end")
        # # rel_width_key = None
        # key_entry.place(relx=0, relwidth=0.5 or 1, width=-1)
        # DETERMINE IF IT'S CREATE OR UPDATE

        # when updating existing list item
        if entry_input_action == ListBoxEntryInputAction.UPDATE.value:
            key_entry = tk.Entry(self, **self.styles['entry'], **self.styles['key_entry'])
             # add the text from the item into the key_entry - just place it but dont allow focus
            key_entry.insert(0, changes_dict.get('key'))
            key_entry.selection_from(0)
            key_entry.selection_to("end")
            key_entry.place(relx=0, y=y_coord, relwidth=0.5 or 1, width=-1)
    
            item_mapped_list: list[str] | None = self._get_config_value_options(changes_dict.get('key'))
            if item_mapped_list:
                option_box = self._handle_value_option_box(
                index=index,
                y_coord=y_coord,
                key_entry=key_entry,
                item_mapped_list=item_mapped_list,
                update_current_selected_item_node_callback=update_current_selected_item_node_callback
                )
                option_box.place(relx=0.3, y=y_coord, relwidth=0.5, width=-1)
                option_box.focus_set()
            else:
                value_entry = tk.Entry(self, **self.styles['entry'])
                value_entry.insert(0, changes_dict.get('value'))
                value_entry.selection_from(0)
                value_entry.selection_to("end")
                value_entry.place(relx=0.3, y=y_coord, relwidth=0.58, width=-1)
                if changes_dict.get('value'):
                    value_entry.focus_set()
                value_entry.bind("<Return>", lambda e: self.accept_edit_to_page_widget(widget=e.widget, index=index, value_entry_widget=e.widget, key_entry_widget=key_entry, update_current_selected_item_node_callback=update_current_selected_item_node_callback))
                for ev in ["<Escape>", "<FocusOut>"]:
                    value_entry.bind(ev, lambda e: self.cancel_update(e.widget, key_entry))
        # when creating new list item w add
        else:
            current_treeview_item = self._get_tree_item_callback()
            current_item_options_list = current_treeview_item.config().keys()
            current_treeview_item = self._get_tree_item_callback()
            current_item_options_list = current_treeview_item.config().keys()
            self._handle_value_option_box(
                index=index,
                key_entry=None,
                item_mapped_list=current_item_options_list,
                update_current_selected_item_node_callback=update_current_selected_item_node_callback
            )
            # use textvariable for key entry 
            key_entry = tk.Entry(self, **self.styles['entry'], **self.styles['key_entry'], textvariable=self.key_var)
            key_entry.selection_from(0)
            key_entry.selection_to("end")
            key_entry.place(relx=0, relwidth=0.5 or 1, width=-1)
            key_entry.focus_set()
            # self.key_var.set(changes_dict.get('key'))
            key_entry.bind("<Return>", self._on_return_create)
            
            # option_box = self._handle_value_option_box(
            # index=index,
            # y_coord=y_coord,
            # key_entry=key_entry,
            # item_mapped_list=item_mapped_list,
            # update_current_selected_item_node_callback=update_current_selected_item_node_callback
            # )
            # option_box.place(relx=0.3, y=y_coord, relwidth=0.5, width=-1)
            # option_box.focus_set()
        # if vals are list use dropdown
        # if self.key_var.get():
        # --- DROP DOWN ENTRY ---
       
        
        # # if no mapping use regular entry
        # else:
        #     print(f"ELSE")
        #      # --- VALUE ENTRY ---
        #     value_entry = tk.Entry(self, **self.styles['entry'], textvariable=self.val_var)
        #     value_entry.insert(0, changes_dict.get('value'))
        #     value_entry.selection_from(0)
        #     value_entry.selection_to("end")
        #     value_entry.place(relx=0.3, y=y_coord, relwidth=0.58, width=-1)
        #     if changes_dict.get('value'):
        #         value_entry.focus_set()
        #     value_entry.bind("<Return>", lambda e: self.accept_edit_to_page_widget(widget=e.widget, index=index, value_entry_widget=e.widget, key_entry_widget=key_entry, update_current_selected_item_node_callback=update_current_selected_item_node_callback))
        #     for ev in ["<Escape>", "<FocusOut>"]:
        #         value_entry.bind(ev, lambda e: self.cancel_update(e.widget, key_entry))
    
    def test(self, *args):
        print(f"### TEST")
        print(f"{self.list_var.get()}")

    def _handle_value_option_box(self, 
        index,
        key_entry,
        item_mapped_list,
        update_current_selected_item_node_callback):
        value_inside = tk.StringVar()
        # set default top value
        value_inside.set(item_mapped_list[0] if item_mapped_list else "")
        # set any list to list var - done to keep it the same across calls
        self.list_var.set(item_mapped_list or [])
        # like bind - get selected value from drop down
        option_box = tk.OptionMenu(self,
            value_inside,
            *self.list_var.get(),
            )
      
        value_inside.trace_add('write', lambda *args:self.accept_edit_to_page_widget(option_box, index, value_entry_widget=value_inside, key_entry_widget=key_entry, update_current_selected_item_node_callback=update_current_selected_item_node_callback))
        # option_box.bind('<Return>', lambda e: self.accept_edit_to_page_widget(widget=e.widget, index=index, value_entry_widget=e.widget, key_entry_widget=key_entry, update_current_selected_item_node_callback=update_current_selected_item_node_callback))
        option_box.bind("<Escape>", lambda e: self.cancel_update(option_box, key_entry))
        # get menu btn parent - only way to detect bind 
        btn = option_box.children['menu'].master
        btn.bind("<FocusOut>", lambda e: self.cancel_update(option_box, key_entry))

        return option_box
        # option_box.place(relx=0.3, y=y_coord, relwidth=0.5, width=-1)
        # option_box.focus_set()
    # get options of config properties to use in dropdown - if they exist
    @staticmethod
    def _get_config_value_options(key_str_value:str=None) -> list| str:
        if not key_str_value:
            return 
        # check for options in map
        options_list = (OPTIONS.get(key_str_value) or {}).get('values')
        if options_list is None:
            logging.debug(f"{key_str_value} not mapped. Using Entry.")
        return options_list
    
    @staticmethod
    def cancel_update(widget, *args):
        widget.destroy()
        for arg in args:
            arg.destroy()
    # handle entry within an entry inside listbox
    # - pass in callback - used in multiple places w diff callbacks
    def accept_edit_to_page_widget(self, 
            widget: tk.Widget, index: int, value_entry_widget: str, key_entry_widget: str, update_current_selected_item_node_callback: callable):
        
        # delete empty entry
        is_val_widget = isinstance(value_entry_widget, tk.Widget) or isinstance(value_entry_widget, tk.StringVar)
        is_key_widget = isinstance(key_entry_widget, tk.Widget)
        if not is_val_widget or not is_key_widget:
            fn = lambda val_type: logging.error(f"No data received for {val_type}. Cancelling edit.")
            fn("value_entry_widget") if not is_val_widget else fn("key_entry_widget")

            self.delete(index)
            self.cancel_update(value_entry_widget, key_entry_widget)
            return

        # delete data at current index and insert new data there
        self.delete(self.editting_item_index)
        self.insert(self.editting_item_index, Utils.build_full_input_str(key_entry_widget.get(), value_entry_widget.get()))
        # send callback to update widget inside treeview
        # - options: set_tree_item_from_entry_value
        k = key_entry_widget.get()
        v = value_entry_widget.get()
        update_current_selected_item_node_callback({
            'key': k,
            'value': v
        })
    
        self.cancel_update(widget, key_entry_widget)
        return v

    def delete_contents(self):
        self.delete(0, tk.END)
    # on init - load selected tree items attrs into listbox
    # runs from treeview
    def insert_all(self, config_dict):
         for key in config_dict:
            # insert selected node into styles_window_listbox window
            display = f"{key}: {config_dict[key]}"
            # this auto sizes w/o adding styles
            self.insert(tk.END, display)

    def insert_item(self, index=tk.END, value=None):
        if value is None:
            logging.info("listbox value is None.")
        self.insert(index, value)

    # set to open on click - only handles open since close is not detectable
    def set_box_state_on_open(self, event):
        # logging.debug(f"state: {self.option_box_state}")
        # if open set to closed - else set to open
        if self.option_box_state == OptionBoxState.CLOSED.value:
            self.option_box_state = OptionBoxState.OPEN.value
            # logging.debug("Option box opened.")
        else:
            self.option_box_state = OptionBoxState.CLOSED.value
            # logging.debug("Option box closed.")