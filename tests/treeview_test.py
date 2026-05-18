import logging
import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from devtools.DevtoolsWindow import DevtoolsWindowKwargs
from devtools.components.observable import Observable
from devtools.components.store import Store
from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager
from devtools.components.widgets.treeview.TreeView import TreeView
from devtools.constants import GeometryType, IS_DEVTOOLS_MARKER, ListboxPageTemplateEnum, TreeStateKey

_TEST_SETTINGS: DevtoolsWindowKwargs = {
    "show_unmapped_widgets": True,
    "devtools_title": "Test",
    "skip_runtime_checks": True,
}


class _DummyStore:
    def __init__(self, mem_store=None):
        self._mem_store = mem_store or {}
        self.tree_refresh_job = None

    def tree_state_get(self, enum_key):
        if enum_key == TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID:
            return self._mem_store
        return None


class _FakeWidget:
    def __init__(self, name, mapped=True, rootx=0, rooty=0, grid=None, place=None):
        self.name = name
        self._mapped = mapped
        self._rootx = rootx
        self._rooty = rooty
        self._grid = grid or {}
        self._place = place or {}

    def __repr__(self):
        return f"FakeWidget({self.name})"

    def winfo_ismapped(self):
        return self._mapped

    def winfo_rootx(self):
        return self._rootx

    def winfo_rooty(self):
        return self._rooty

    def grid_info(self):
        return self._grid

    def place_info(self):
        return self._place


class _FakeParent:
    def __init__(self, children, pack_slaves):
        self._children = children
        self._pack_slaves = pack_slaves

    def winfo_children(self):
        return self._children

    def pack_slaves(self):
        return self._pack_slaves

    def update_idletasks(self):
        return None


class TreeViewTests(unittest.TestCase):
    def test_is_devtools_widget_detects_marker_in_parent_chain(self):
        root = SimpleNamespace(devtools_marker=IS_DEVTOOLS_MARKER, master=None)
        child = SimpleNamespace(master=root)
        tree = TreeView.__new__(TreeView)

        self.assertTrue(tree._is_devtools_widget(child))

    def test_is_relevant_tree_event_widget_detects_ancestor_in_mem_store(self):
        tracked_parent = SimpleNamespace(master=None)
        leaf = SimpleNamespace(master=tracked_parent)
        tree = TreeView.__new__(TreeView)
        tree._store = _DummyStore(mem_store={id(tracked_parent): {"tree_id": "I001"}})

        self.assertTrue(tree._is_relevant_tree_event_widget(leaf))

    def test_schedule_tree_refresh_queues_once(self):
        tree = TreeView.__new__(TreeView)
        tree._store = _DummyStore()
        tree.after_idle = Mock(return_value="job-id")
        tree.rebuild_tree_from_root = Mock()

        tree.schedule_tree_refresh()
        tree.schedule_tree_refresh()

        self.assertEqual(tree._store.tree_refresh_job, "job-id")
        tree.after_idle.assert_called_once()

    def test_handle_tcl_event_emit_schedules_refresh_for_relevant_widget(self):
        root = tk.Tk()
        root.withdraw()
        try:
            frame = tk.Frame(root)
            tree = TreeView.__new__(TreeView)
            tree._store = SimpleNamespace(tree_applying_highlight=False)
            tree._is_devtools_widget = Mock(return_value=False)
            tree._is_relevant_tree_event_widget = Mock(return_value=True)
            tree.schedule_tree_refresh = Mock()
    
            tree.handle_tcl_event_emit(SimpleNamespace(widget=frame))

            tree.schedule_tree_refresh.assert_called_once()
        finally:
            root.destroy()

    def test_handle_tcl_event_emit_ignores_non_tk_widget(self):
        tree = TreeView.__new__(TreeView)
        tree.schedule_tree_refresh = Mock()

        tree.handle_tcl_event_emit(SimpleNamespace(widget=object()))

        tree.schedule_tree_refresh.assert_not_called()

    def test_tree_order_key_prefers_mapped_root_coordinates(self):
        child = _FakeWidget("a", mapped=True, rootx=40, rooty=20)
        children = [child]
        tree = TreeView.__new__(TreeView)

        key = tree.tree_order_key(child=child, children=children, pack_order={})

        self.assertEqual(key, (0, 20, 40, 0))

    def test_tree_order_key_grid_fallback(self):
        child = _FakeWidget("g", mapped=False, grid={"row": "2", "column": "3"})
        tree = TreeView.__new__(TreeView)
        geo_info = SimpleNamespace(geometry_type=GeometryType.GRID)

        with patch("devtools.components.widgets.treeview.TreeView.Utils.build_widget_geometry_manager_info", return_value=geo_info):
            key = tree.tree_order_key(child=child, children=[child], pack_order={})

        self.assertEqual(key, (1, 2, 3, 0))

    def test_tree_order_key_pack_fallback_uses_pack_order(self):
        child = _FakeWidget("p", mapped=False)
        tree = TreeView.__new__(TreeView)
        geo_info = SimpleNamespace(geometry_type=GeometryType.PACK)

        with patch("devtools.components.widgets.treeview.TreeView.Utils.build_widget_geometry_manager_info", return_value=geo_info):
            key = tree.tree_order_key(child=child, children=[child], pack_order={child: 7})

        self.assertEqual(key, (1, 7, 0))

    def test_get_display_ordered_children_keeps_unmapped_slots(self):
        mapped_first = _FakeWidget("first", mapped=True)
        unmapped_middle = _FakeWidget("middle", mapped=False)
        mapped_last = _FakeWidget("last", mapped=True)
        parent = _FakeParent(
            children=[mapped_first, unmapped_middle, mapped_last],
            pack_slaves=[mapped_first, mapped_last],
        )
        tree = TreeView.__new__(TreeView)

        def reverse_order_for_mapped(child, children, pack_order):
            return 1 if child is mapped_first else 0

        tree.tree_order_key = reverse_order_for_mapped

        ordered = tree.get_display_ordered_children(parent)

        self.assertEqual(ordered, [mapped_last, unmapped_middle, mapped_first])


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Shared fixture: real Tk root + TreeView wired to a real Store + listboxes
# ---------------------------------------------------------------------------

class _TreeFixture(unittest.TestCase):
    def setUp(self):
        self.trace_patcher = patch.object(logging, "trace", create=True)
        self.low_trace_patcher = patch.object(logging, "low_trace", create=True)
        self.trace_patcher.start()
        self.low_trace_patcher.start()

        self.root = tk.Tk()
        self.root.withdraw()
        self.frame_a = tk.Frame(self.root)
        self.frame_a.pack()
        self.label_b = tk.Label(self.root)
        self.label_b.pack()

        self.observable = Observable()
        self.store = Store(observable=self.observable, **_TEST_SETTINGS)

        container = tk.Frame(self.root)
        self.options_lb = ConfigListboxManager(
            master=container,
            listbox_page_template_enum=ListboxPageTemplateEnum.OPTIONS,
            observable=self.observable,
            store=self.store,
        )
        self.geometry_lb = ConfigListboxManager(
            master=container,
            listbox_page_template_enum=ListboxPageTemplateEnum.GEOMETRY,
            observable=self.observable,
            store=self.store,
        )
        self.store.listbox_templates = {
            ListboxPageTemplateEnum.OPTIONS: self.options_lb,
            ListboxPageTemplateEnum.GEOMETRY: self.geometry_lb,
        }
        self.store.current_listbox_template = self.options_lb

        parent_frame = tk.Frame(self.root)
        self.tree = TreeView(
            master=self.root,
            parent=parent_frame,
            observable=self.observable,
            store=self.store,
        )
        self.root.update_idletasks()

    def tearDown(self):
        self.root.destroy()
        self.trace_patcher.stop()
        self.low_trace_patcher.stop()


# ---------------------------------------------------------------------------
# Tree build: items inserted + both stores populated
# ---------------------------------------------------------------------------

class TreeBuildTests(_TreeFixture):

    def test_root_node_appears_in_tree(self):
        self.assertGreater(len(self.tree.get_children()), 0)

    def test_mem_id_store_contains_root(self):
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        self.assertIn(id(self.root), mem)

    def test_tree_insert_id_store_maps_root_tree_id_to_root_widget(self):
        root_tid = self.tree.get_children()[0]
        widget = self.store.tree_state_get(
            TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT
        ).get(root_tid)
        self.assertIs(widget, self.root)

    def test_children_appear_as_tree_descendants(self):
        root_tid = self.tree.get_children()[0]
        id_map = self.store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT)
        widgets = {id_map.get(d) for d in self.tree.get_children(root_tid)}
        self.assertIn(self.frame_a, widgets)
        self.assertIn(self.label_b, widgets)

    def test_mem_id_entry_contains_frozen_config_snapshot(self):
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        entry = mem.get(id(self.frame_a))
        self.assertIsNotNone(entry)
        self.assertIsInstance(entry.get("widget_config_init_frozen"), dict)

    def test_devtools_marker_widget_excluded_on_rebuild(self):
        marked = tk.Frame(self.root)
        marked.devtools_marker = IS_DEVTOOLS_MARKER
        marked.pack()
        self.root.update_idletasks()
        self.tree.delete_tree()
        self.store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, {})
        self.store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, {})
        self.tree.build_tree(self.root)
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        self.assertNotIn(id(marked), mem)

    def test_unmapped_widget_excluded_when_show_unmapped_false(self):
        self.store.show_unmapped_widgets = False
        hidden = tk.Frame(self.root)  # not packed
        self.tree.delete_tree()
        self.store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, {})
        self.store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, {})
        self.tree.build_tree(self.root)
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        self.assertNotIn(id(hidden), mem)

    def test_unmapped_widget_included_when_show_unmapped_true(self):
        self.store.show_unmapped_widgets = True
        hidden = tk.Frame(self.root)  # not packed
        self.tree.delete_tree()
        self.store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, {})
        self.store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, {})
        self.tree.build_tree(self.root)
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        self.assertIn(id(hidden), mem)


# ---------------------------------------------------------------------------
# delete_tree and rebuild
# ---------------------------------------------------------------------------

class DeleteAndRebuildTests(_TreeFixture):

    def test_delete_tree_removes_all_nodes(self):
        self.tree.delete_tree()
        self.assertEqual(len(self.tree.get_children()), 0)

    def test_rebuild_repopulates_after_delete(self):
        self.tree.delete_tree()
        self.store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, {})
        self.store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, {})
        self.tree.build_tree(self.root)
        self.assertGreater(len(self.tree.get_children()), 0)

    def test_rebuild_from_master_resets_in_progress_flag(self):
        self.tree.rebuild_tree_from_master_root()
        self.assertFalse(self.store.tree_rebuild_in_progress)

    def test_rebuild_from_master_clears_refresh_job(self):
        self.tree.rebuild_tree_from_master_root()
        self.assertIsNone(self.store.tree_refresh_job)

    def test_rebuild_while_in_progress_sets_requested_flag(self):
        self.store.tree_rebuild_in_progress = True
        self.tree.rebuild_tree_from_master_root()
        self.assertTrue(self.store.tree_rebuild_requested)
        self.store.tree_rebuild_in_progress = False
        self.store.tree_rebuild_requested = False

    def test_rebuild_preserves_selection_for_surviving_widget(self):
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        entry = mem.get(id(self.frame_a))
        if not entry:
            return
        self.tree.selection_set(entry["tree_id"])
        self.store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, self.frame_a)
        self.tree.rebuild_tree_from_master_root()
        self.root.update_idletasks()
        sel = self.tree.selection()
        if sel:
            widget = self.store.tree_state_get(
                TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT
            ).get(sel[0])
            self.assertIs(widget, self.frame_a)


# ---------------------------------------------------------------------------
# Store lookup helpers
# ---------------------------------------------------------------------------

class StoreLookupTests(_TreeFixture):

    def test_get_widget_by_tree_insert_id_returns_root(self):
        root_tid = self.tree.get_children()[0]
        self.assertIs(self.tree.get_widget_by_tree_insert_id(root_tid), self.root)

    def test_get_widget_by_obj_mem_id_returns_root(self):
        self.assertIs(self.tree.get_widget_by_obj_mem_id(id(self.root)), self.root)

    def test_add_tree_item_writes_correct_tree_id_and_widget(self):
        dummy = tk.Frame(self.root)
        dummy.pack()
        self.root.update_idletasks()
        self.tree.add_tree_item_to_obj_mem_id_store(id(dummy), "I_TEST", dummy)
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        entry = mem.get(id(dummy))
        self.assertIsNotNone(entry)
        self.assertEqual(entry["tree_id"], "I_TEST")
        self.assertIs(entry["widget"], dummy)


# ---------------------------------------------------------------------------
# Highlight apply / remove
# ---------------------------------------------------------------------------

class HighlightTests(_TreeFixture):

    def test_apply_sets_highlighted_widget(self):
        with patch.object(self.tree, "_show_highlight_overlay", return_value=False):
            self.tree._apply_highlight(self.frame_a)
            self.root.update_idletasks()
        self.assertIs(self.store.tree_highlighted_widget, self.frame_a)

    def test_apply_saves_config(self):
        with patch.object(self.tree, "_show_highlight_overlay", return_value=False):
            self.tree._apply_highlight(self.frame_a)
            self.root.update_idletasks()
        self.assertIsNotNone(self.store.tree_highlight_saved_config)

    def test_remove_clears_highlighted_widget(self):
        with patch.object(self.tree, "_show_highlight_overlay", return_value=False):
            self.tree._apply_highlight(self.frame_a)
            self.root.update_idletasks()
        self.tree._remove_highlight()
        self.assertIsNone(self.store.tree_highlighted_widget)

    def test_remove_clears_saved_config(self):
        with patch.object(self.tree, "_show_highlight_overlay", return_value=False):
            self.tree._apply_highlight(self.frame_a)
            self.root.update_idletasks()
        self.tree._remove_highlight()
        self.assertIsNone(self.store.tree_highlight_saved_config)

    def test_config_strategy_restores_original_highlightthickness(self):
        original = self.frame_a.cget("highlightthickness")
        with patch.object(self.tree, "_show_highlight_overlay", return_value=False):
            self.tree._apply_highlight(self.frame_a)
            self.root.update_idletasks()
        self.tree._remove_highlight()
        self.assertEqual(self.frame_a.cget("highlightthickness"), original)

    def test_remove_with_nothing_highlighted_does_not_raise(self):
        self.store.tree_highlighted_widget = None
        self.store.tree_highlight_saved_config = None
        try:
            self.tree._remove_highlight()
        except Exception as exc:
            self.fail(f"_remove_highlight raised unexpectedly: {exc}")

    def test_hide_overlay_calls_place_forget_on_all_edges(self):
        edges = [Mock(winfo_exists=Mock(return_value=True)) for _ in range(4)]
        self.store.tree_highlight_overlay_edges = edges
        self.tree._hide_highlight_overlay()
        for edge in edges:
            edge.place_forget.assert_called_once()


# ---------------------------------------------------------------------------
# handle_tcl_event_emit — all filtering paths
# ---------------------------------------------------------------------------

class TclEventEmitTests(unittest.TestCase):

    def setUp(self):
        self.trace_patcher = patch.object(logging, "trace", create=True)
        self.trace_patcher.start()

    def tearDown(self):
        self.trace_patcher.stop()

    def _tree(self):
        t = TreeView.__new__(TreeView)
        t._store = SimpleNamespace(tree_applying_highlight=False)
        t.schedule_tree_refresh = Mock()
        return t

    def test_non_tk_widget_ignored(self):
        t = self._tree()
        t.handle_tcl_event_emit(SimpleNamespace(widget=object()))
        t.schedule_tree_refresh.assert_not_called()

    def test_none_widget_ignored(self):
        t = self._tree()
        t.handle_tcl_event_emit(SimpleNamespace(widget=None))
        t.schedule_tree_refresh.assert_not_called()

    def test_devtools_widget_skipped(self):
        root = tk.Tk()
        root.withdraw()
        try:
            frame = tk.Frame(root)
            t = self._tree()
            t._is_devtools_widget = Mock(return_value=True)
            t._is_relevant_tree_event_widget = Mock(return_value=True)
            t.handle_tcl_event_emit(SimpleNamespace(widget=frame))
            t.schedule_tree_refresh.assert_not_called()
        finally:
            root.destroy()

    def test_highlight_in_progress_suppresses_refresh(self):
        root = tk.Tk()
        root.withdraw()
        try:
            frame = tk.Frame(root)
            t = self._tree()
            t._store.tree_applying_highlight = True
            t._is_devtools_widget = Mock(return_value=False)
            t._is_relevant_tree_event_widget = Mock(return_value=True)
            t.handle_tcl_event_emit(SimpleNamespace(widget=frame))
            t.schedule_tree_refresh.assert_not_called()
        finally:
            root.destroy()

    def test_relevant_tk_widget_schedules_refresh(self):
        root = tk.Tk()
        root.withdraw()
        try:
            frame = tk.Frame(root)
            t = self._tree()
            t._is_devtools_widget = Mock(return_value=False)
            t._is_relevant_tree_event_widget = Mock(return_value=True)
            t.handle_tcl_event_emit(SimpleNamespace(widget=frame))
            t.schedule_tree_refresh.assert_called_once()
        finally:
            root.destroy()

    def test_irrelevant_tk_widget_does_not_schedule_refresh(self):
        root = tk.Tk()
        root.withdraw()
        try:
            frame = tk.Frame(root)
            t = self._tree()
            t._is_devtools_widget = Mock(return_value=False)
            t._is_relevant_tree_event_widget = Mock(return_value=False)
            t.handle_tcl_event_emit(SimpleNamespace(widget=frame))
            t.schedule_tree_refresh.assert_not_called()
        finally:
            root.destroy()


# ---------------------------------------------------------------------------
# Options listbox state stuffing
# ---------------------------------------------------------------------------

class StuffOptionsStateTests(_TreeFixture):

    def test_options_state_is_populated_as_dict(self):
        self.store.current_listbox_template = self.options_lb
        self.tree.stuff_listbox_options_state_into_page_template(self.frame_a)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.OPTIONS
        ]["current_values_state"]
        self.assertIsInstance(state, dict)
        self.assertGreater(len(state), 0)

    def test_options_state_contains_relief(self):
        self.store.current_listbox_template = self.options_lb
        self.tree.stuff_listbox_options_state_into_page_template(self.frame_a)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.OPTIONS
        ]["current_values_state"]
        self.assertIn("relief", state)

    def test_options_values_are_not_raw_tk_config_tuples(self):
        # conform_option_lisbox_config must unwrap (name, db_name, class, default, current)
        self.store.current_listbox_template = self.options_lb
        self.tree.stuff_listbox_options_state_into_page_template(self.frame_a)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.OPTIONS
        ]["current_values_state"]
        for key, val in state.items():
            self.assertNotIsInstance(val, tuple,
                f"Option '{key}' must be unwrapped, not a raw tuple: {val!r}")

    def test_options_keys_are_sorted_alphabetically(self):
        self.store.current_listbox_template = self.options_lb
        self.tree.stuff_listbox_options_state_into_page_template(self.frame_a)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.OPTIONS
        ]["current_values_state"]
        keys = list(state.keys())
        self.assertEqual(keys, sorted(keys))


# ---------------------------------------------------------------------------
# Geometry listbox state stuffing
# ---------------------------------------------------------------------------

class StuffGeometryStateTests(_TreeFixture):

    def test_geometry_state_includes_visibility(self):
        self.store.current_listbox_template = self.geometry_lb
        self.tree.stuff_listbox_geometry_state_into_page_template(self.frame_a)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.GEOMETRY
        ]["current_values_state"]
        self.assertTrue(
            any("visibility" in k for k in state),
            f"Missing visibility key, got: {list(state.keys())}"
        )

    def test_geometry_state_includes_geometry_type(self):
        self.store.current_listbox_template = self.geometry_lb
        self.tree.stuff_listbox_geometry_state_into_page_template(self.frame_a)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.GEOMETRY
        ]["current_values_state"]
        self.assertTrue(
            any("geometry" in k for k in state),
            f"Missing geometry type key, got: {list(state.keys())}"
        )

    def test_unmapped_widget_has_no_pack_grid_specific_keys(self):
        unmapped = tk.Frame(self.root)  # not packed
        self.store.current_listbox_template = self.geometry_lb
        self.tree.stuff_listbox_geometry_state_into_page_template(unmapped)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.GEOMETRY
        ]["current_values_state"]
        self.assertNotIn("fill", state)
        self.assertNotIn("row", state)
        self.assertNotIn("side", state)

    def test_packed_widget_state_includes_fill(self):
        self.store.current_listbox_template = self.geometry_lb
        self.tree.stuff_listbox_geometry_state_into_page_template(self.frame_a)
        state = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.GEOMETRY
        ]["current_values_state"]
        self.assertTrue(
            any("fill" in k for k in state),
            f"Expected fill key for packed widget, got: {list(state.keys())}"
        )


# ---------------------------------------------------------------------------
# update_tree_item_to_page_widget_* — real widget mutations
# ---------------------------------------------------------------------------

class UpdateWidgetConfigTests(_TreeFixture):

    def test_option_config_applies_relief_to_widget(self):
        self.store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, self.frame_a)
        self.tree.update_tree_item_to_page_widget_option_config(key="relief", value="groove")
        self.assertEqual(self.frame_a.cget("relief"), "groove")

    def test_pack_config_applies_expand_to_widget(self):
        self.store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, self.frame_a)
        self.tree.update_tree_item_to_page_widget_pack_config(key="expand", value=True)
        self.assertEqual(str(self.frame_a.pack_info().get("expand")), "1")

    def test_grid_config_applies_row_to_widget(self):
        # Use a dedicated sub-frame so grid doesn't conflict with the pack manager on root
        grid_container = tk.Frame(self.root)
        grid_container.pack()
        gf = tk.Frame(grid_container)
        gf.grid(row=0, column=0)
        self.store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, gf)
        self.tree.update_tree_item_to_page_widget_grid_config(key="row", value=3)
        self.assertEqual(str(gf.grid_info().get("row")), "3")

    def test_place_config_applies_x_to_widget(self):
        pf = tk.Frame(self.root)
        pf.place(x=10, y=10)
        self.store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, pf)
        self.tree.update_tree_item_to_page_widget_place_config(key="x", value=99)
        self.assertEqual(str(pf.place_info().get("x")), "99")