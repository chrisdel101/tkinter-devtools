from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import logging

from devtools.components.observable import Action
from devtools.constants import ActionType, ListboxInsertNotifyStateKey, ListboxPageInsertEnum, TreeStateKey
from devtools.decorators import try_except_catcher
from devtools.utils import Utils
from devtools.config import app_config


class TreeView(ttk.Treeview):

    def __init__(self, root, parent, observable, store):
        super().__init__(parent, show="tree", style="My.Treeview")
        self.root = root
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

        self.selection_set(self.get_children()[0])
        # self.event_generate("<<TreeviewSelect>>")

    # store the ID and use to retrieve with self.selection()
    def add_tree_item_to_tree_insert_id_store(self, item_id, widget):
        """Store the widget by Treeview.insert ID."""
        current_widget_id_dict = self._store.tree_state_get(
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT)
        new_dict = {**current_widget_id_dict, **{item_id: widget}}

        self._store.tree_state_set(
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, new_dict)
        # self.store_widget_by_tree_insert_id[item_id] = widget

    # store mem id() like {4579038880: {tree_id:'I002', widget:tk.Widget}}
    def add_tree_item_to_obj_mem_id_store(self, memory_id: int, tree_insert_id: str, widget: tk.Widget):
        # """Store the widget by Treeview.insert ID."""
        # self.store_widget_by_obj_mem_id[memory_id] = {
        #     "tree_id": tree_insert_id,
        #      "widget": widget
        #     }
        # get current id(widget) state
        current_mem_id_widget_state = self._store.tree_state_get(
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        # merge new state with exising state
        new_dict = Utils.merge_dicts(
            current_mem_id_widget_state,
            {memory_id: {
                "tree_id": tree_insert_id,
                "widget": widget,
                "widget_config_init_frozen": Utils.conform_option_lisbox_config(Utils.filter_non_used_config_options(widget.configure()))
            }})
        # overwrite existing state with new
        self._store.tree_state_set(
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, new_dict)

    def get_widget_by_tree_insert_id(self, item_id: str):
        return self._store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT).get(item_id)

    def get_widget_by_obj_mem_id(self, item_id: int):
        return self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID).get(item_id).get("widget")

    # on first call insert widget and get insert id - recurse
    # on next calls used vals passed in
    def build_tree(self, parent_widget: tk.Widget, parent_widget_insert_id: str = ""):
        try:
            # if no parent node it's first call - no id to use yet
            if not parent_widget_insert_id:
                parent_memory_id = id(parent_widget)
                # manual insert - get insert id
                # set using blank str for parent - used for first node in the tree w no parent
                # insert at end index
                insert_parent_memory_id = self.insert_item(
                    parent_item_id="", index=tk.END, widget=parent_widget)
                # add using mem id {4579038880: {tree_id:'I002', widget:tk.Widget}}
                self.add_tree_item_to_obj_mem_id_store(
                    parent_memory_id, insert_parent_memory_id, parent_widget)
                self.add_tree_item_to_tree_insert_id_store(
                    insert_parent_memory_id, parent_widget)

            else:
                # parent node - so use id passed from prev call - it's parent for this call
                insert_parent_memory_id = parent_widget_insert_id
            # method gives all child widgets of tk obj
            for child in parent_widget.winfo_children():
                # dev tools window - skip this top level in tree
                if isinstance(child, tk.Toplevel) and child._name == app_config['top_level_name']:
                    continue
                # hide unmapped widgets - optionalaå
                if not self._store.show_unmapped_widgets and not child.winfo_ismapped():
                    continue
                child_memory_id = id(child)
                # ID of place in tree - insert returns tree insert ID
                insert_child_memory_id = self.insert_item(
                    parent_item_id=insert_parent_memory_id, index=tk.END, widget=child)
                self.add_tree_item_to_obj_mem_id_store(
                    child_memory_id, insert_child_memory_id, child)
                # dict store id: widget
                self.add_tree_item_to_tree_insert_id_store(
                    insert_child_memory_id, child)
                self.build_tree(child, insert_child_memory_id)

        except Exception as e:
            logging.error(f"Error build_tree: {e}")
            raise e

    # walk the tree and get all the widgets
    def collect_widgets(self, widget, acc=None):
        try:
            if acc is None:
                acc = set()
            if not self.get_widget_by_obj_mem_id(id(widget)):
                self.delete_tree()
                # change - rebuild tree
                self.build_tree(self.root)
                return
            else:
                acc.add(widget)

            for child in widget.winfo_children():
                if not isinstance(child, tk.Toplevel):
                    if not self.get_widget_by_obj_mem_id(id(child)):
                        self.delete_tree()
                        # change - rebuild tree
                        self.build_tree(self.root)
                        return
                    else:
                        self.collect_widgets(child, acc)

            return acc
        except Exception as e:
            logging.error(f"Error collect_widgets: {e}")
            raise

    def handle_tree_select(self, _,):
        try:
            collect_widgets = self.collect_widgets(self.root)
            self.root.update_idletasks()
            # get selected tree item viatree api
            selected_tree_id = self.selection()
            if selected_tree_id and selected_tree_id != self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET):
                # .selection give tree insert item ID
                item_id = selected_tree_id[0]
                # set tree state selected item
                self._store.tree_state_set(
                    TreeStateKey.SELECTED_ITEM_WIDGET, self.get_widget_by_tree_insert_id(item_id))
                # mem_obj_id = self.get_widget_by_obj_mem_id(id(self._store.tree_state_get('selected_item')))

                # TODO check if current select is already selected
                if selected_item_widget := self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET):
                    try:
                        # HANDLE OPTION COMBOBOX INSERT
                        # delete prev content in listbox
                        self._observable.notify_observers(
                            Action(type=ActionType.DELETE_ALL_LISTBOX_ITEMS))
                        # config used to populate listbox
                        original_options_config: dict = self._store.tree_state_get(
                            TreeStateKey.SELECTED_ITEM_WIDGET).configure()
                        # filter out unwanted config values not in ConfigOptionName - keep original dict formating
                        filtered_config_dict: dict[str, tuple] = Utils.filter_non_used_config_options(
                            original_options_config)
                        # extract the actual set value from value tuples - is key val str pairs
                        key_value_config_dict: dict[str, str] = Utils.conform_option_lisbox_config(
                            filtered_config_dict)
                        key_value_config_sorted_dict = Utils.sorted_dict(
                            key_value_config_dict)
                        # save listbox state - diff than listbox insert into UI
                        self._store.listbox_manager_state_set(enum_key=ListboxInsertNotifyStateKey.CURRENT_VALUES_STATE,
                        state_to_set=key_value_config_sorted_dict, page_insert_override=ListboxPageInsertEnum.OPTIONS)
                        # HANDLE GEOMETRY LISTBOX INSERT
                        # if widget has no geometry set false to hide window button
                        # GeometryOptionAddition
                        self._store.show_geometry_button = (bool(Utils.get_geometry_manager_info(selected_item_widget)))
                        # self._store.handle_toggle_geometry_btn(bool(Utils.get_geometry_info(selected_item_widget)))
                        widget_geometry_dict: dict =Utils.resolve_geometry_aliases(Utils.combine_additional_geometry_ooptions(selected_item_widget))
                        sorted_widget_geometry_dict = Utils.sorted_dict(widget_geometry_dict)
                        # set geometry listbox state
                        self._store.listbox_manager_state_set(enum_key=ListboxInsertNotifyStateKey.CURRENT_VALUES_STATE,
                                                              state_to_set=sorted_widget_geometry_dict, page_insert_override=ListboxPageInsertEnum.GEOMETRY)

                    except Exception as e:
                        err_msg = f"error handle_tree_select: {e}"
                        logging.error(err_msg, exc_info=True)
                        # delete all listbox
                        self._observable.notify_observers(
                            Action(type=ActionType.DELETE_ALL_LISTBOX_ITEMS))
                        # post the error to the screen
                        self._observable.notify_observers(Action(
                            type=ActionType.INSERT_LISTBOX_ITEM, data={'index': tk.END, 'value': err_msg}))

        except Exception as e:
            logging.error(f"Error handle_tree_select: {e}", exc_info=True)

    @try_except_catcher
    # listbox calls to make updates to grid geomtetry
    def update_tree_item_to_page_widget_grid_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        current_tree_item.grid_configure(
            **{listbox_item_pairs_dict['key']: listbox_item_pairs_dict['value']})
        current_tree_item.update_idletasks()

    @try_except_catcher
    # listbox calls to make updates to place geomtetry
    def update_tree_item_to_page_widget_place_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        current_tree_item.place_configure(
            **{listbox_item_pairs_dict['key']: listbox_item_pairs_dict['value']})

    @try_except_catcher
    # listbox calls to make updates to pack geomtetry
    def update_tree_item_to_page_widget_pack_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        current_tree_item.pack_configure(
            **{listbox_item_pairs_dict['key']: listbox_item_pairs_dict['value']})

    # listbox calls to make updates to widget options
    # - UPDATE THE PAGE WIDGET HERE
    @try_except_catcher
    def update_tree_item_to_page_widget_option_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        # for invalid entry error proporates to top and stops execution
        current_tree_item.config(
            **{listbox_item_pairs_dict['key']: listbox_item_pairs_dict['value']})

    # delete tree and all branches
    def delete_tree(self):
        self.delete(*self.get_children())
    # insert item into treeview

    def insert_item(self, parent_item_id, index: str, widget: tk.Widget):
        tree_insert_id = self.insert(
            parent_item_id, index, text=widget.winfo_class())
        return tree_insert_id

    def notify(self, action: Action):
        Utils.dispatch_action(self, action)
