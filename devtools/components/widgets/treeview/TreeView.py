from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from devtools.logging_utils import logger
from devtools.decorators.decorators import class_fn_try_except_catcher
from devtools.components.observable import Action
from devtools.constants import IS_DEVTOOLS_SENTINEL, ActionType, CommonGeometryOption, GeometryType, ListboxPageTemplateEnum, TreeStateKey
from devtools.geometry_info import GeometryManagerInfo
from devtools.maps import CONFIG_OPTION_SETTINGS
from devtools.components.widgets.treeview.TreeViewUtils import TreeViewUtils
from devtools.components.widgets.treeview.TreeViewHighlighter import TreeViewHighlighter
from devtools.utils import Utils


class TreeView(ttk.Treeview):

    @class_fn_try_except_catcher
    # Initialize the TreeView widget, build the tree, and set the initial selection.
    def __init__(self, master, parent, observable, store):
        super().__init__(parent, show="tree", style="My.Treeview")
        self._app = master
        self._observable = observable
        self._store = store
        self._observable.register_observer(self)
        self._highlighter = TreeViewHighlighter(self, observable, store)
        # "#0" is special built-in first column - width of 300
        self.column("#0", width=300)
        self.bind("<<TreeviewSelect>>", self._handle_tree_select)
        # originals kept across rebuilds
        self._carried_frozen_config_by_mem_id: dict[int, dict] = {}
        self._build_tree(master)
        self._bind_tree_change_events()
        # tree destroyed - cancel its queued rebuild and remove its bindings and border from the app
        self.bind("<Destroy>", self._cleanup_on_tree_destroy, add=True)
        # select the first tree item - trigger the listbox build
        self.selection_set(self.get_children()[0])

    @class_fn_try_except_catcher
    # Bind Map, Unmap, and Destroy on the app window to watch for widget tree change - like when pages are changed
    def _bind_tree_change_events(self):
        self._app_window = self._app.winfo_toplevel()
        # keep each bind id - unbind(sequence, funcid) removes only ours and keeps the app's own handlers
        self._app_bind_ids = {
            sequence: self._app_window.bind(sequence, self._handle_tcl_event_emit, add=True)
            for sequence in ("<Map>", "<Unmap>", "<Destroy>")
        }

    @class_fn_try_except_catcher
    # Tree destroyed - cancel its queued rebuild and remove its bindings and border from the app
    def _cleanup_on_tree_destroy(self, _):
        # queued rebuild would run on the dead tree
        if self._store.tree_refresh_job is not None:
            self.after_cancel(self._store.tree_refresh_job)
            self._store.tree_refresh_job = None
        for sequence, funcid in self._app_bind_ids.items():
            self._app_window.unbind(sequence, funcid)
        self._highlighter.destroy_highlight_overlay()

    @class_fn_try_except_catcher
    # Return True if the widget or any ancestor belongs to the devtools window vs appS
    def _is_devtools_widget(self, widget: tk.Widget) -> bool:
        current = widget
        while current is not None:
            if getattr(current, "devtools_marker", None) == IS_DEVTOOLS_SENTINEL:
                return True
            current = getattr(current, "master", None)
        return False
    
    @class_fn_try_except_catcher
    def _is_relevant_tree_event_widget(self, widget: tk.Widget) -> bool:
        # Only refresh when event is from current tree nodes or descendants of them.
        mem_store = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID) or {}
        current = widget
        while current is not None:
            if id(current) in mem_store:
                return True
            current = getattr(current, "master", None)
        return False

    # Filter widget tree events and schedule a refresh if the source is relevant - comes from tcl when these events are emitted
    @class_fn_try_except_catcher
    def _handle_tcl_event_emit(self, event):
        event_widget = getattr(event, "widget", None)
        if event_widget is None or not isinstance(event_widget, tk.BaseWidget):
            return
        if self._is_devtools_widget(event_widget):
            return
        if self._store.is_tree_applying_highlight:
            return
        if not self._is_relevant_tree_event_widget(event_widget):
            return
        self._schedule_tree_refresh()

    @class_fn_try_except_catcher
    # Schedule a single deferred tree rebuild, ignoring duplicate pending requests.
    def _schedule_tree_refresh(self):
        if getattr(self._store, "tree_rebuild_in_progress", False):
            self._store.tree_rebuild_requested = True
            return
        if self._store.tree_refresh_job is not None:
            return
        self._store.tree_refresh_job = self.after_idle(self._rebuild_tree_from_master_root)

    @class_fn_try_except_catcher
    # Rebuild the full widget tree from root, restoring expanded nodes and selection - allows page changes
    def _rebuild_tree_from_master_root(self):
        if getattr(self._store, "tree_rebuild_in_progress", False):
            self._store.tree_rebuild_requested = True
            return

        self._store.tree_rebuild_in_progress = True
        self._store.tree_refresh_job = None
        try:
            mem_store = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID) or {}
            expanded_mem_ids = {
                mem_id for mem_id, entry in mem_store.items()
                if (tree_id := entry.get("tree_id")) and self.exists(tree_id) and self.item(tree_id, "open")
            }
            selected_widget = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET)
            # rebuild re-reads the live config, so carry the originals
            self._carried_frozen_config_by_mem_id = {
                mem_id: entry["widget_config_init_frozen"] for mem_id, entry in mem_store.items()
                if entry.get("widget") is not None and entry["widget"].winfo_exists()
            }
            self.delete_tree()
            self._store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, {})
            self._store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, {})
            self._build_tree(self._app)

            mem_store = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID) or {}
            for mem_id in expanded_mem_ids:
                if entry := mem_store.get(mem_id):
                    if tree_id := entry.get("tree_id"):
                        if self.exists(tree_id):
                            self.item(tree_id, open=True)

            if selected_widget and selected_widget.winfo_exists():
                selected_item = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID).get(id(selected_widget))
                if selected_item and self.exists(selected_item.get("tree_id")):
                    self.selection_set(selected_item.get("tree_id"))
            elif self.get_children():
                self.selection_set(self.get_children()[0])
        finally:
            self._carried_frozen_config_by_mem_id = {}
            self._store.tree_rebuild_in_progress = False
            if getattr(self._store, "tree_rebuild_requested", False):
                self._store.tree_rebuild_requested = False
                self._schedule_tree_refresh()

    # store the ID and use to retrieve with self.selection()
    @class_fn_try_except_catcher
    def _add_tree_item_to_tree_insert_id_store(self, item_id, widget):
        """Store the widget by Treeview.insert ID."""
        current_widget_id_dict = self._store.tree_state_get(
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT)
        new_dict = {**current_widget_id_dict, **{item_id: widget}}

        self._store.tree_state_set(
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, new_dict)

    # store mem id() like {4579038880: {tree_id:'I002', widget:tk.Widget}}
    @class_fn_try_except_catcher
    def _add_tree_item_to_obj_mem_id_store(self, memory_id: int, tree_insert_id: str, widget: tk.Widget):
        # get current id(widget) state
        current_mem_id_widget_state = self._store.tree_state_get(
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        # merge new state with exising state
        new_dict = Utils.merge_dicts(
            current_mem_id_widget_state,
            {memory_id: {
                "tree_id": tree_insert_id,
                "widget": widget,
                "widget_config_init_frozen": self._carried_frozen_config_by_mem_id.get(memory_id)
                    or Utils.conform_option_lisbox_config(Utils.filter_non_used_config_options(widget.configure()))
            }})
        # overwrite existing state with new
        self._store.tree_state_set(
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, new_dict)

    # Return the widget stored under the given Treeview insert ID.
    def _get_widget_by_tree_insert_id(self, item_id: str):
        return self._store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT).get(item_id)

    # Return a sort key ordering a child widget by visual position with geometry fallbacks.
    @class_fn_try_except_catcher
    def _tree_order_key(
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
        # on tcl failure - get widget coords using the geometry managaer
        geo_manager_info = Utils.build_widget_geometry_manager_info(child)

        # Fallback for grid-managed widgets: row/column order
        if geo_manager_info and geo_manager_info.geometry_type == GeometryType.GRID:
            info = child.grid_info()
            row = TreeViewUtils.safe_int(info.get("row"), 0)
            column = TreeViewUtils.safe_int(info.get("column"), 0)
            return (1, row, column, original_index)

        # Fallback for pack-managed widgets: Tk pack sibling order
        if geo_manager_info and geo_manager_info.geometry_type == GeometryType.PACK:
            order = pack_order.get(child, original_index)
            return (1, order, original_index)

        # Fallback for place-managed widgets: y/x coordinates
        if geo_manager_info and geo_manager_info.geometry_type == GeometryType.PLACE:
            info = child.place_info()
            y = TreeViewUtils.safe_int(info.get("y"), 0)
            x = TreeViewUtils.safe_int(info.get("x"), 0)
            return (1, y, x, original_index)

        # Final fallback: keep original sibling declaration order
        return (2, original_index)

    @class_fn_try_except_catcher
    # Return children of parent_widget sorted by their visible display order.
    def _get_display_ordered_children(self, parent_widget: tk.Widget) -> list[tk.Widget]:
        # Raw sibling order from Tk (creation/declaration order under this parent)
        children = list(parent_widget.winfo_children())
        if not children:
            logger.trace(f"No children for widget: {parent_widget} with id {id(parent_widget)}")
            return children

        # Ensure widget geometry/position info is up to date before visual sorting
        parent_widget.update_idletasks()
        # Pack sibling order is used as a fallback inside _tree_order_key
        pack_order = {
            child: index for index, child in enumerate(parent_widget.pack_slaves())
        }

        # Only mapped widgets are visually sortable by actual display position
        mapped_children = [child for child in children if child.winfo_ismapped()]
        mapped_children_sorted = sorted(
            mapped_children,
            key=lambda child: self._tree_order_key(
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
    @class_fn_try_except_catcher
    def _build_tree(self, parent_widget: tk.Widget, parent_widget_insert_id: str = ""):
        # if no parent node it's first call - no id to use yet
        if not parent_widget_insert_id:
            parent_memory_id = id(parent_widget)
            # manual insert - get insert id
            # set using blank str for parent - used for first node in the tree w no parent
            # insert at end index
            insert_parent_memory_id = self._insert_item(
                parent_item_id="", index=tk.END, widget=parent_widget)
            # add using mem id {4579038880: {tree_id:'I002', widget:tk.Widget}}
            self._add_tree_item_to_obj_mem_id_store(
                parent_memory_id, insert_parent_memory_id, parent_widget)
            self._add_tree_item_to_tree_insert_id_store(
                insert_parent_memory_id, parent_widget)

        else:
            # parent node - so use id passed from prev call - it's parent for this call
            insert_parent_memory_id = parent_widget_insert_id
        # method gives all child widgets of tk obj
        for child in self._get_display_ordered_children(parent_widget):
            # skip the devtools window branch
            if getattr(child, "devtools_marker", None) == IS_DEVTOOLS_SENTINEL:
                continue
            # hide unmapped widgets - optional
            if not self._store.show_unmapped_widgets and not child.winfo_ismapped():
                continue
            child_memory_id = id(child)
            # ID of place in tree - insert returns tree insert ID
            insert_child_memory_id = self._insert_item(
                parent_item_id=insert_parent_memory_id, index=tk.END, widget=child)
            self._add_tree_item_to_obj_mem_id_store(
                child_memory_id, insert_child_memory_id, child)
            # dict store id: widget
            self._add_tree_item_to_tree_insert_id_store(
                insert_child_memory_id, child)
            self._build_tree(child, insert_child_memory_id)


    @class_fn_try_except_catcher
    # Handle a Treeview selection event and update the highlight and listbox state.
    def _handle_tree_select(self, _,):
        # get selected tree item via tree api
        selected_tree_id = self.selection()
        if selected_tree_id:
            # .selection gives tree insert item ID
            item_id = selected_tree_id[0]
            incoming_widget = self._get_widget_by_tree_insert_id(item_id)
            # skip if same widget is already selected
            if incoming_widget is self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET):
                return
            # set tree state selected item
            self._store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, incoming_widget)

            if selected_item_widget := self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET):
            # inner try except handles fatal-type select/build errors
                try:
                    # HANDLE OPTION LISTBOX TEMPLATE
                    self._stuff_listbox_options_state_into_page_template(selected_item_widget)
                    # HANDLE GEOMETRY LISTBOX INSERT
                    self._stuff_listbox_geometry_state_into_page_template(selected_item_widget)

                    self._store.show_geometry_button = (bool(Utils.build_widget_geometry_manager_info(selected_item_widget)))
                
                except Exception as e:
                    err_msg = f"error _handle_tree_select: {e}"
                    logger.error(err_msg, exc_info=True)
                    # delete all listbox
                    self._observable.notify_observers(
                        Action(type=ActionType.DELETE_ALL_LISTBOX_ITEMS))
                    # post the error to the screen
                    self._observable.notify_observers(Action(
                        type=ActionType.INSERT_LISTBOX_ITEM, data={'index': tk.END, 'value': err_msg}))
                # highlight after listing options - else the list shows the highlight border
                self._highlighter.apply_highlight(selected_item_widget)

    # ---- LIST WIDGETS VALUES HERE----
    # Populate the options listbox page with the selected widget's configure values.
    def _stuff_listbox_options_state_into_page_template(self, selected_item_widget):
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
        # resolve image internal name (e.g. pyimage8) to the file path it was loaded from
        key_value_config_dict = Utils.resolve_image_name_to_path(selected_item_widget, key_value_config_dict)
        # redraw width and height with the redrawn size - if page is stale
        key_value_config_dict = Utils.resolve_drawn_size(selected_item_widget, key_value_config_dict)
        # sort by alpha order
        key_value_config_sorted_dict = Utils.sorted_dict(
            key_value_config_dict)
        # stuff listbox state template state values
        self._store.listbox_manager_template_values_state_set(
            state_to_set=key_value_config_sorted_dict,  page_insert_override=ListboxPageTemplateEnum.OPTIONS)

    # Populate the geometry listbox page with the selected widget's geometry values.
    def _stuff_listbox_geometry_state_into_page_template(self, selected_item_widget):

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
        self._store.listbox_manager_template_values_state_set(
        state_to_set=sorted_widget_geometry_dict, page_insert_override=ListboxPageTemplateEnum.GEOMETRY)

    @class_fn_try_except_catcher
    # listbox calls to make updates to grid geomtetry
    def update_tree_item_to_page_widget_grid_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        current_tree_item.grid_configure(
            **{listbox_item_pairs_dict['key']: listbox_item_pairs_dict['value']})
        current_tree_item.update_idletasks()
        return True

    @class_fn_try_except_catcher
    # listbox calls to make updates to place geomtetry
    def update_tree_item_to_page_widget_place_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        current_tree_item.place_configure(
            **{listbox_item_pairs_dict['key']: listbox_item_pairs_dict['value']})
        return True

    @class_fn_try_except_catcher
    # listbox calls to make updates to pack geomtetry
    def update_tree_item_to_page_widget_pack_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        current_tree_item.pack_configure(
            **{listbox_item_pairs_dict['key']: listbox_item_pairs_dict['value']})
        return True

    @class_fn_try_except_catcher
    # listbox calls to make updates to widget options
    # - UPDATE THE PAGE WIDGET HERE
    def update_tree_item_to_page_widget_option_config(self, **listbox_item_pairs_dict):
        # self is the page widget - updates the config
        current_tree_item = self._store.tree_state_get(
            TreeStateKey.SELECTED_ITEM_WIDGET)
        key, value = listbox_item_pairs_dict['key'], listbox_item_pairs_dict['value']
        # listbox gives text - convert number options, some widgets only take numbers
        value_type = CONFIG_OPTION_SETTINGS.get(key, {}).get('type')
        if value_type in (int, float) and isinstance(value, str):
            try:
                value = value_type(value)
            except ValueError:
                # swallow value errors - handled in decorator
                pass
        # if textvariable is set  update the variable instead of tex
        if key == 'text' and 'textvariable' in current_tree_item.keys() and current_tree_item.cget('textvariable'):
            current_tree_item.setvar(str(current_tree_item.cget('textvariable')), value)
            return True
        # for invalid entry error proporates to top and stops execution
        current_tree_item.config(**{key: value})
        return True

    @class_fn_try_except_catcher
    # delete tree and all branches
    def delete_tree(self):
        self.delete(*self.get_children())
        
    @class_fn_try_except_catcher
    # insert item into treeview
    def _insert_item(self, parent_item_id, index: str, widget: tk.Widget):
        tree_insert_id = self.insert(
            parent_item_id, index, text=widget.winfo_class())
        return tree_insert_id

    @class_fn_try_except_catcher
    # Dispatch incoming observable actions to the matching handler on this widget.
    def notify(self, action: Action):
        return Utils.dispatch_action(self, action)
