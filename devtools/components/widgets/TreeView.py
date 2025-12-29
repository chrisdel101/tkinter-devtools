from __future__ import annotations
import tkinter as tk
from tkinter import ttk 
import logging

from devtools.components.observable import Action
from devtools.constants import ListboxManagerStateKey, TreeStateKey
from devtools.utils import Utils

class TreeView(ttk.Treeview):
    
    def __init__(self, root, master, observable, store, listbox_widget): 
        super().__init__(master, show="tree", style="My.Treeview")
        self.root = root
        self.selected_item = None
        self._listbox_widget = listbox_widget
        self._observable = observable
        self._store = store
        self._observable.register_observer(self)
        # use Treeview.insert id like 'I001'
        # self.store_widget_by_tree_insert_id: dict[str, tk.Widget] = {}
        # use obj mem id from id(obj) - {id: {tree_id:str, widget:tk.Widget}}
        # self.store_widget_by_obj_mem_id: dict[int, dict[str,tk.Widget]] = {}
        self.column("#0", width=300)
        # main listener for tree item selects
        self.bind("<<TreeviewSelect>>", self.handle_tree_select)
        self.build_tree(root)
        # on init use tree selection_set api - triggers lb load
        self.selection_set(self.get_children()[0])

    # store the ID and use to retrieve with self.selection()
    def add_tree_item_to_tree_insert_id_store(self, item_id, widget):
        """Store the widget by Treeview.insert ID."""
        current_widget_id_dict = self._store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT) 
        new_dict = {**current_widget_id_dict, **{item_id: widget}}
        
        self._store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, new_dict)
        # self.store_widget_by_tree_insert_id[item_id] = widget

    # store mem id() like {4579038880: {tree_id:'I002', widget:tk.Widget}}
    def add_tree_item_to_obj_mem_id_store(self, memory_id: int, tree_insert_id: str, widget: tk.Widget):
        # """Store the widget by Treeview.insert ID."""
        # self.store_widget_by_obj_mem_id[memory_id] = {
        #     "tree_id": tree_insert_id, 
        #      "widget": widget
        #     }
        current_mem_id_widget_store = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID) 
        new_dict = Utils.merge_dicts(
            current_mem_id_widget_store, 
            {memory_id: {
                "tree_id": tree_insert_id, 
                "widget": widget,
                "widget_config_init_frozen": Utils.extract_current_config_key_values(Utils.filter_non_used_config_attrs(widget.configure()))
            }})
        self._store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, new_dict)

    def get_widget_by_tree_insert_id(self, item_id: str):
        return self._store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT).get(item_id)

    def get_widget_by_obj_mem_id(self, item_id: int):
        return self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID).get(item_id).get("widget")
    
    # on first call insert widget and get insert id - recurse
    # on next calls used vals passed in 
    def build_tree(self, parent_widget: tk.Widget, parent_widget_insert_id: str=""):
        try:
            # no parent node it's first call - no id to use yet
            if not parent_widget_insert_id:
                parent_memory_id = id(parent_widget)
                # manual insert -get insert id
                # set using blank str   - used for first level tree node
                insert_parent_memory_id = self.insert("", "end", text=parent_widget.winfo_class())
                # add using mem id {4579038880: {tree_id:'I002', widget:tk.Widget}}
                self.add_tree_item_to_obj_mem_id_store(parent_memory_id, insert_parent_memory_id, parent_widget)
                self.add_tree_item_to_tree_insert_id_store(insert_parent_memory_id, parent_widget) 
               
            else:
            # parent node - so use id passed from prev call
                insert_parent_memory_id = parent_widget_insert_id
            # method gives all child widgets of tk obj
            for child in parent_widget.winfo_children():
                # Skip any Toplevel windows - this is the dev tool window
                if isinstance(child, tk.Toplevel):
                    continue
                child_memory_id = id(child)
                  # check not already stored - build the tree
                  # if it is stored = no change just move on
               
                # ID of place in tree - insert returns ID of inserted widget
                insert_child_memory_id = self.insert(insert_parent_memory_id, "end", text=child.winfo_class())
                self.add_tree_item_to_obj_mem_id_store(child_memory_id, insert_child_memory_id, child)
                # dict store id: widget 
                self.add_tree_item_to_tree_insert_id_store(insert_child_memory_id, child)
                self.build_tree(child, insert_child_memory_id)
              
        except Exception as e:
            logging.error(f"Error building tree: {e}")


    # walk the tree and get all the widgets  
    def collect_widgets(self, widget, acc=None):
        try:
            if acc is None:
                acc = set()
            if not self.get_widget_by_obj_mem_id(id(widget)):
                self.delete_tree()
                # change - rebuild tree 
                self.build_tree(self.root)
                return "break"
            else:
                acc.add(widget)

            for child in widget.winfo_children():
                if not isinstance(child, tk.Toplevel):
                    if not self.get_widget_by_obj_mem_id(id(child)):   
                        self.delete_tree()
                        # change - rebuild tree 
                        self.build_tree(self.root)
                        return "break"  
                    else:
                        self.collect_widgets(child, acc)

            return acc
        except Exception as e:
            logging.error(f"Error collecting widgets: {e}") 

    def handle_tree_select(self, _,):
        try:
            collect_widgets = self.collect_widgets(self.root)
            # get selected tree item via tree api
            selected = self.selection()
            if selected and selected != self._store.tree_state_get(TreeStateKey.SELECTED_ITEM):    
                # .selection give tree insert item ID
                item_id = selected[0]
                # set tree state selected item
                self._store.tree_state_set(TreeStateKey.SELECTED_ITEM, self.get_widget_by_tree_insert_id(item_id))
                # mem_obj_id = self.get_widget_by_obj_mem_id(id(self._store.tree_state_get('selected_item')))
                
                # TODO check if current select is already selected
                if self._store.tree_state_get(TreeStateKey.SELECTED_ITEM):
                    try:
                        # delete prev content in listbox
                        self._listbox_widget._delete()
                        # config used to populate listbox
                        original_config = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM).configure()
                        # filter out unwanted config values - keep original format
                        filtered_config_dict: dict[str, tuple] = Utils.filter_non_used_config_attrs(original_config)
                        # extract the actual set value from value tuples - is key val str pairs
                        key_value_config_dict: dict[str, str] = Utils.extract_current_config_key_values(filtered_config_dict)
                        key_value_config_sorted_dict = Utils.sorted_dict(key_value_config_dict)
                        # set store current listbox value state
                        self._store.listbox_manager_state_set(enum_key=ListboxManagerStateKey.CURRENT_VALUES_STATE, state_to_set=key_value_config_sorted_dict)

                    except Exception as e:
                        self._listbox_widget._delete()
                        # post the error to the screen
                        self._listbox_widget.insert(tk.END, f"Error: {e}")
        except Exception as e:
            logging.error(f"Error handling tree select: {e}", exc_info=True)

    # takes a dict and applies it to widget config
    # - UPDATE THE PAGE WIDGET HERE
    def update_tree_item_to_page_widget(self, changes_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM)
        current_tree_item.config(**{changes_dict['key']: changes_dict['value']})

    # delete tree and all branches
    def delete_tree(self):
        self.delete(*self.get_children())

    def notify(self, action: Action):
        Utils.dispatch_action(self, action)

        
        