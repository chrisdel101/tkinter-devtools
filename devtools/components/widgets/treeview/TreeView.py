from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import logging

from devtools.components.observable import Action
from devtools.constants import ActionType, CommonGeometryOption, GeometryType, ListboxTemplateNotifyStateKey, ListboxPageTemplateEnum, TreeStateKey
from devtools.decorators import try_except_catcher
from devtools.geometry_info import GeometryManagerInfo
from devtools.components.widgets.treeview.TreeViewUtils import TreeViewUtils
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


    def tree_order_key(
        self,
        child: tk.Widget,
        children: list[tk.Widget],
        pack_order: dict[tk.Widget, int],
    ):
        # preserve sibling declaration order as a stable tie-breaker
        original_index = children.index(child)
        
        # First preference: if widget is visible, sort by actual on-screen position
        # (top-to-bottom, then left-to-right)
        if child.winfo_ismapped():
            try:
                return (0, child.winfo_rooty(), child.winfo_rootx(), original_index)
            except tk.TclError:
                # if runtime position cannot be read, fall through to geometry-based ordering
                pass

        geo_manager_info = Utils.build_widget_geometry_manager_info(child)

        # Fallback for grid-managed widgets: row/column order
        if geo_manager_info and geo_manager_info.geometry_type == GeometryType.GRID:
            info = child.grid_info()
            row = TreeViewUtils._safe_int(info.get("row"), 0)
            column = TreeViewUtils._safe_int(info.get("column"), 0)
            return (1, row, column, original_index)

        # Fallback for pack-managed widgets: Tk pack sibling order
        if geo_manager_info and geo_manager_info.geometry_type == GeometryType.PACK:
            order = pack_order.get(child, original_index)
            return (1, order, original_index)

        # Fallback for place-managed widgets: y/x coordinates
        if geo_manager_info and geo_manager_info.geometry_type == GeometryType.PLACE:
            info = child.place_info()
            y = TreeViewUtils._safe_int(info.get("y"), 0)
            x = TreeViewUtils._safe_int(info.get("x"), 0)
            return (1, y, x, original_index)

        # Final fallback: keep original sibling declaration order
        return (2, original_index)

    def get_display_ordered_children(self, parent_widget: tk.Widget) -> list[tk.Widget]:
        # Raw sibling order from Tk (creation/declaration order under this parent)
        children = list(parent_widget.winfo_children())
        if not children:
            logging.debug(f"No children for widget: {parent_widget} with id {id(parent_widget)}")
            return children

        # Ensure widget geometry/position info is up to date before visual sorting
        parent_widget.update_idletasks()
        # Pack sibling order is used as a fallback inside tree_order_key
        pack_order = {
            child: index for index, child in enumerate(parent_widget.pack_slaves())
        }

        # Only mapped widgets are visually sortable by actual display position
        mapped_children = [child for child in children if child.winfo_ismapped()]
        mapped_children_sorted = sorted(
            mapped_children,
            key=lambda child: self.tree_order_key(
                child=child,
                children=children,
                pack_order=pack_order,
            ),
        )

        # Rebuild final list by replacing mapped slots with sorted mapped widgets,
        # while keeping unmapped widgets in their original sibling positions.
        mapped_iter = iter(mapped_children_sorted)
        ordered_children: list[tk.Widget] = []
        for child in children:
            if child.winfo_ismapped():
                ordered_children.append(next(mapped_iter))
            else:
                ordered_children.append(child)

        return ordered_children

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
            for child in self.get_display_ordered_children(parent_widget):
                # dev tools window - skip this top level in tree
                if isinstance(child, tk.Toplevel) and child._name == app_config['top_level_name']:
                    continue
                # hide unmapped widgets - optional
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
                        # HANDLE OPTION LISTBOX TEMPLATE
                        self.stuff_listbox_options_state_into_page_template(selected_item_widget)
                        # HANDLE GEOMETRY LISTBOX INSERT
                        self.stuff_listbox_geometry_state_into_page_template(selected_item_widget)

                        self._store.show_geometry_button = (bool(Utils.build_widget_geometry_manager_info(selected_item_widget)))

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
    def stuff_listbox_options_state_into_page_template(self, selected_item_widget):
        # delete prev content in listbox
        self._observable.notify_observers(
            Action(type=ActionType.DELETE_ALL_LISTBOX_ITEMS))
        # get configure vals - these will populate the list box
        original_options_config: dict = selected_item_widget.configure()
        # filter out unwanted config values not in ConfigOptionName - keep original dict formating
        filtered_config_dict: dict[str, tuple] = Utils.filter_non_used_config_options(
            original_options_config)
        # extract the actual set value from value tuples 
        # - is key val str pairs
        key_value_config_dict: dict[str, str] = Utils.conform_option_lisbox_config(
            filtered_config_dict)
        # sort by alpha order
        key_value_config_sorted_dict = Utils.sorted_dict(
            key_value_config_dict)
        # stuff listbox state template state values
        self._store.listbox_manager_state_set(
            enum_key=ListboxTemplateNotifyStateKey.CURRENT_VALUES_STATE,
            state_to_set=key_value_config_sorted_dict,  page_insert_override=ListboxPageTemplateEnum.OPTIONS)

    @try_except_catcher
    def stuff_listbox_geometry_state_into_page_template(self, selected_item_widget):

        current_widget_geo_manager: GeometryManagerInfo = Utils.build_widget_geometry_manager_info(selected_item_widget)
        current_geo_type = getattr(current_widget_geo_manager, 'geometry_type', None)
        sibling_geo_type = TreeViewUtils.check_sibling_geometry_type(selected_item_widget)
        # set this to sibling type if unmapped - allows options to use when mapping from UI
        resolved_geo_type = sibling_geo_type if current_geo_type == GeometryType.UNMAPPED and sibling_geo_type else current_geo_type
        # set type it could be if setting unmapped to mapped - must match sibling
        geo_type_and_visibility_dict = {
            CommonGeometryOption.GEOMETRY_TYPE: getattr(resolved_geo_type, 'value', resolved_geo_type),
            CommonGeometryOption.VISIBILITY: selected_item_widget.winfo_ismapped()
        }

        if current_geo_type == GeometryType.UNMAPPED:
            combined_with_widget_geometry_options = geo_type_and_visibility_dict
        else:
            combined_with_widget_geometry_options = Utils.combine_additional_geometry_options(
                geo_manager=current_widget_geo_manager,
                **geo_type_and_visibility_dict,
            )
        
        widget_geometry_dict: dict = Utils.resolve_geometry_aliases(
            combined_with_widget_geometry_options)
        sorted_widget_geometry_dict = Utils.sorted_dict(
            widget_geometry_dict)
        # set geometry listbox state
        self._store.listbox_manager_state_set(enum_key=ListboxTemplateNotifyStateKey.CURRENT_VALUES_STATE,
        state_to_set=sorted_widget_geometry_dict, page_insert_override=ListboxPageTemplateEnum.GEOMETRY)

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
