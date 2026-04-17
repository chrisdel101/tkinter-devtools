from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import logging

from devtools.components.observable import Action
from devtools.constants import IS_DEVTOOLS_MARKER, ActionType, CommonGeometryOption, GeometryType, ListboxTemplateNotifyStateKey, ListboxPageTemplateEnum, TreeStateKey
from devtools.decorators import try_except_catcher
from devtools.geometry_info import GeometryManagerInfo
from devtools.components.widgets.treeview.TreeViewUtils import TreeViewUtils
from devtools.utils import Utils


class TreeView(ttk.Treeview):

    # Initialize the TreeView widget, build the tree, and set the initial selection.
    def __init__(self, master, parent, observable, store):
        super().__init__(parent, show="tree", style="My.Treeview")
        self.master = master
        self._observable = observable
        self._store = store
        self._observable.register_observer(self)
        # "#0" is special built-in first column - width of 300
        self.column("#0", width=300)
        self.bind("<<TreeviewSelect>>", self.handle_tree_select)
        self.build_tree(master)
        self._bind_tree_change_events()
        # select the first tree item - trigger the listbox build
        self.selection_set(self.get_children()[0])

    # Bind Map, Unmap, and Destroy on master to watch for widget tree changes.
    def _bind_tree_change_events(self):
        self.master.bind_all("<Map>", self.handle_tcl_event_emit, add=True)
        self.master.bind_all("<Unmap>", self.handle_tcl_event_emit, add=True)
        self.master.bind_all("<Destroy>", self.handle_tcl_event_emit, add=True)

    # Return True if the widget or any ancestor belongs to the devtools window.
    def _is_devtools_widget(self, widget: tk.Widget) -> bool:
        current = widget
        while current is not None:
            if getattr(current, "devtools_marker", None) == IS_DEVTOOLS_MARKER:
                return True
            current = getattr(current, "master", None)
        return False

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
    def handle_tcl_event_emit(self, event):
        event_widget = getattr(event, "widget", None)
        if event_widget is None or not isinstance(event_widget, tk.BaseWidget):
            return
        if self._is_devtools_widget(event_widget):
            return
        if self._store.tree_applying_highlight:
            return
        if not self._is_relevant_tree_event_widget(event_widget):
            return
        self.schedule_tree_refresh()

    # Schedule a single deferred tree rebuild, ignoring duplicate pending requests.
    def schedule_tree_refresh(self):
        if self._store.tree_refresh_job is not None:
            return
        self._store.tree_refresh_job = self.after_idle(self.rebuild_tree_from_master_root)

    # Rebuild the full widget tree from root, restoring expanded nodes and selection - allows page changes 
    def rebuild_tree_from_master_root(self):
        self._store.tree_refresh_job = None
        mem_store = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID) or {}
        expanded_mem_ids = {
            mem_id for mem_id, entry in mem_store.items()
            if (tree_id := entry.get("tree_id")) and self.item(tree_id, "open")
        }
        selected_widget = self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET)
        self.delete_tree()
        self._store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, {})
        self._store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, {})
        self.build_tree(self.master)

        mem_store = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID) or {}
        for mem_id in expanded_mem_ids:
            if entry := mem_store.get(mem_id):
                if tree_id := entry.get("tree_id"):
                    self.item(tree_id, open=True)

        if selected_widget and selected_widget.winfo_exists():
            selected_item = self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID).get(id(selected_widget))
            if selected_item:
                self.selection_set(selected_item.get("tree_id"))
        elif self.get_children():
            self.selection_set(self.get_children()[0])

    # store the ID and use to retrieve with self.selection()
    def add_tree_item_to_tree_insert_id_store(self, item_id, widget):
        """Store the widget by Treeview.insert ID."""
        current_widget_id_dict = self._store.tree_state_get(
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT)
        new_dict = {**current_widget_id_dict, **{item_id: widget}}

        self._store.tree_state_set(
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, new_dict)

    # store mem id() like {4579038880: {tree_id:'I002', widget:tk.Widget}}
    def add_tree_item_to_obj_mem_id_store(self, memory_id: int, tree_insert_id: str, widget: tk.Widget):
        # """Store the widget by Treeview.insert ID."""
        current_by_mem_id = self._store.tree_store_widget_by_obj_mem_id or {}
        current_by_mem_id[memory_id] = {
            "tree_id": tree_insert_id,
             "widget": widget
            }
        self._store.tree_store_widget_by_obj_mem_id = current_by_mem_id
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

    # Return the widget stored under the given Treeview insert ID.
    def get_widget_by_tree_insert_id(self, item_id: str):
        return self._store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT).get(item_id)

    # Return the widget stored under the given Python object memory ID.
    def get_widget_by_obj_mem_id(self, item_id: int):
        return self._store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID).get(item_id).get("widget")

    # Return a sort key ordering a child widget by visual position with geometry fallbacks.
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

    # Return children of parent_widget sorted by their visible display order.
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
    @try_except_catcher
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
                # skip the devtools window branch
                if getattr(child, "devtools_marker", None) == IS_DEVTOOLS_MARKER:
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

    # Highlight the selected widget using an overlay frame or a direct config fallback.
    def _apply_highlight(self, widget: tk.Widget):
        self._store.tree_applying_highlight = True
        self._remove_highlight()
        try:
            if self._show_highlight_overlay(widget):
                self._store.tree_highlight_saved_config = {'strategy': 'overlay'}
                self._store.tree_highlighted_widget = widget
            else:
                # Fallback to direct widget config only if overlay cannot be placed.
                self._store.tree_highlight_saved_config = {
                    'strategy': 'config',
                    'config': {
                        'highlightbackground': widget.cget('highlightbackground'),
                        'highlightthickness': widget.cget('highlightthickness'),
                    },
                }
                widget.configure(highlightbackground='#FF4500', highlightthickness=2)
                self._store.tree_highlighted_widget = widget
        except tk.TclError:
            self._store.tree_highlight_saved_config = None
        # Clear flag after_idle so queued Tk events from configure fire while flag is still True
        self.after_idle(self._clear_applying_highlight)

    # Remove the highlight from the previously highlighted widget.
    def _remove_highlight(self):
        if self._store.tree_highlighted_widget and self._store.tree_highlight_saved_config:
            try:
                strategy = self._store.tree_highlight_saved_config.get('strategy')
                if strategy == 'overlay':
                    self._hide_highlight_overlay()
                elif strategy == 'config':
                    self._store.tree_highlighted_widget.configure(**self._store.tree_highlight_saved_config.get('config', {}))
            except tk.TclError:
                pass
        self._hide_highlight_overlay()
        self._store.tree_highlighted_widget = None
        self._store.tree_highlight_saved_config = None

    # Place four thin Frame edges around the widget to draw a highlight border overlay.
    def _show_highlight_overlay(self, widget: tk.Widget) -> bool:
        if not widget.winfo_exists():
            return False
        parent = getattr(widget, 'master', None)
        if parent is None:
            return False

        widget.update_idletasks()
        x = widget.winfo_x()
        y = widget.winfo_y()
        width = widget.winfo_width()
        height = widget.winfo_height()

        if width <= 1 or height <= 1:
            return False

        if (
            len(self._store.tree_highlight_overlay_edges) != 4
            or any(not edge.winfo_exists() for edge in self._store.tree_highlight_overlay_edges)
            or self._store.tree_highlight_overlay_parent is not parent
        ):
            self._hide_highlight_overlay()
            self._store.tree_highlight_overlay_parent = parent
            self._store.tree_highlight_overlay_edges = [
                tk.Frame(parent, bg='#FF4500', bd=0, highlightthickness=0)
                for _ in range(4)
            ]

        border_size = 2
        top_edge, right_edge, bottom_edge, left_edge = self._store.tree_highlight_overlay_edges

        top_edge.place(
            x=x,
            y=y,
            width=width,
            height=border_size,
        )
        right_edge.place(
            x=x + max(width - border_size, 0),
            y=y,
            width=border_size,
            height=height,
        )
        bottom_edge.place(
            x=x,
            y=y + max(height - border_size, 0),
            width=width,
            height=border_size,
        )
        left_edge.place(
            x=x,
            y=y,
            width=border_size,
            height=height,
        )

        # Keep border visible while not covering the widget interior.
        for edge in self._store.tree_highlight_overlay_edges:
            edge.lift(widget)
        return True

    # Hide all overlay edge frames by removing them from the layout.
    def _hide_highlight_overlay(self):
        for edge in self._store.tree_highlight_overlay_edges:
            if edge.winfo_exists():
                edge.place_forget()

    # Clear the applying-highlight guard flag after queued Tk events have been processed.
    def _clear_applying_highlight(self):
        self._store.tree_applying_highlight = False

    # Handle a Treeview selection event and update the highlight and listbox state.
    def handle_tree_select(self, _,):
        try:
            # get selected tree item via tree api
            selected_tree_id = self.selection()
            if selected_tree_id:
                # .selection gives tree insert item ID
                item_id = selected_tree_id[0]
                incoming_widget = self.get_widget_by_tree_insert_id(item_id)
                # skip if same widget is already selected
                if incoming_widget is self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET):
                    return
                # set tree state selected item
                self._store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, incoming_widget)

                if selected_item_widget := self._store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET):
                    self._apply_highlight(selected_item_widget)
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
    # Populate the options listbox page with the selected widget's configure values.
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
    # Populate the geometry listbox page with the selected widget's geometry values.
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

    # Dispatch incoming observable actions to the matching handler on this widget.
    def notify(self, action: Action):
        Utils.dispatch_action(self, action)
