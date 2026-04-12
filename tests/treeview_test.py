import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from devtools.components.widgets.treeview.TreeView import TreeView
from devtools.constants import GeometryType, IS_DEVTOOLS_MARKER, TreeStateKey


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

    def test_on_widget_tree_event_schedules_refresh_for_relevant_widget(self):
        root = tk.Tk()
        root.withdraw()
        try:
            frame = tk.Frame(root)
            tree = TreeView.__new__(TreeView)
            tree._store = SimpleNamespace(tree_applying_highlight=False)
            tree._is_devtools_widget = Mock(return_value=False)
            tree._is_relevant_tree_event_widget = Mock(return_value=True)
            tree.schedule_tree_refresh = Mock()

            tree._on_widget_tree_event(SimpleNamespace(widget=frame))

            tree.schedule_tree_refresh.assert_called_once()
        finally:
            root.destroy()

    def test_on_widget_tree_event_ignores_non_tk_widget(self):
        tree = TreeView.__new__(TreeView)
        tree.schedule_tree_refresh = Mock()

        tree._on_widget_tree_event(SimpleNamespace(widget=object()))

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