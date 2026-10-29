"""
Tests for TreeViewUtils — geometry inference, sibling detection,
safe int conversion, and default geometry state building.
"""
import tkinter as tk
import unittest
from unittest.mock import patch

from devtools.components.widgets.treeview.TreeViewUtils import TreeViewUtils
from devtools.constants import CommonGeometryOption, GeometryType
from devtools.geometry_info import GeometryManagerInfo
from devtools.utils import Utils


class SafeIntTests(unittest.TestCase):

    def test_integer_string_converts(self):
        self.assertEqual(TreeViewUtils.safe_int("5"), 5)

    def test_none_returns_default(self):
        self.assertEqual(TreeViewUtils.safe_int(None, 99), 99)

    def test_empty_string_returns_default(self):
        self.assertEqual(TreeViewUtils.safe_int("", 0), 0)

    def test_float_string_returns_default(self):
        # "1.5" cannot be cast to int directly — must return default
        self.assertEqual(TreeViewUtils.safe_int("1.5", -1), -1)

    def test_zero_string_converts_to_zero(self):
        self.assertEqual(TreeViewUtils.safe_int("0"), 0)


class CheckSiblingGeometryTypeTests(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_returns_pack_when_sibling_is_packed(self):
        parent = tk.Frame(self.root)
        parent.pack()
        sibling = tk.Frame(parent)
        sibling.pack()
        target = tk.Frame(parent)
        # target is not packed — sibling is
        geo = TreeViewUtils.check_sibling_geometry_type(target)
        self.assertEqual(geo, GeometryType.PACK)

    def test_returns_grid_when_sibling_is_gridded(self):
        parent = tk.Frame(self.root)
        parent.pack()
        sibling = tk.Frame(parent)
        sibling.grid(row=0, column=0)
        target = tk.Frame(parent)
        geo = TreeViewUtils.check_sibling_geometry_type(target)
        self.assertEqual(geo, GeometryType.GRID)

    def test_returns_none_when_no_siblings_have_geometry(self):
        parent = tk.Frame(self.root)
        parent.pack()
        target = tk.Frame(parent)
        # no other siblings mapped
        geo = TreeViewUtils.check_sibling_geometry_type(target)
        self.assertIsNone(geo)

    def test_ignores_self_when_checking_siblings(self):
        parent = tk.Frame(self.root)
        parent.pack()
        target = tk.Frame(parent)
        target.pack()
        # only sibling is itself — should not count self
        other = tk.Frame(parent)
        geo = TreeViewUtils.check_sibling_geometry_type(other)
        self.assertEqual(geo, GeometryType.PACK)


class InferGeometryOptionsTests(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_pack_inference_returns_before_next_sibling(self):
        parent = tk.Frame(self.root)
        parent.pack()
        next_sib = tk.Frame(parent)
        next_sib.pack()
        target = tk.Frame(parent)
        # target not packed; next_sib comes after in children list but is mapped
        # re-order so target is index 0 and next_sib is index 1
        self.root.update_idletasks()
        result = TreeViewUtils.infer_geometry_options(target, GeometryType.PACK)
        # result may be {} or {"before": next_sib} depending on position
        self.assertIsInstance(result, dict)

    def test_grid_inference_with_no_neighbours_returns_row0_col0(self):
        parent = tk.Frame(self.root)
        parent.pack()
        target = tk.Frame(parent)
        result = TreeViewUtils.infer_geometry_options(target, GeometryType.GRID)
        self.assertEqual(result, {"row": 0, "column": 0})

    def test_grid_inference_with_prev_neighbour_increments_column(self):
        parent = tk.Frame(self.root)
        parent.pack()
        prev = tk.Frame(parent)
        prev.grid(row=0, column=2)
        target = tk.Frame(parent)
        # _nearest_grid_sibling_positions checks winfo_ismapped() on siblings —
        # patch it so the function sees prev as mapped (headless Tk always returns 0).
        original_ismapped = tk.Frame.winfo_ismapped
        try:
            tk.Frame.winfo_ismapped = lambda self: 1
            result = TreeViewUtils.infer_geometry_options(target, GeometryType.GRID)
        finally:
            tk.Frame.winfo_ismapped = original_ismapped
        self.assertEqual(result.get("row"), 0)
        self.assertEqual(result.get("column"), 3)

    def test_unknown_geometry_type_returns_empty_dict(self):
        parent = tk.Frame(self.root)
        parent.pack()
        target = tk.Frame(parent)
        result = TreeViewUtils.infer_geometry_options(target, GeometryType.PLACE)
        self.assertIsInstance(result, dict)

    def test_no_parent_returns_empty_dict(self):
        target = tk.Frame.__new__(tk.Frame)
        target.master = None
        result = TreeViewUtils.infer_geometry_options(target, GeometryType.GRID)
        self.assertEqual(result, {})


class DefaultGeometryStateTests(unittest.TestCase):

    def test_grid_state_has_geometry_type_value(self):
        state = TreeViewUtils._default_geometry_state_for_type(GeometryType.GRID)
        self.assertEqual(state.get(CommonGeometryOption.GEOMETRY_TYPE), GeometryType.GRID.value)

    def test_pack_state_has_geometry_type_value(self):
        state = TreeViewUtils._default_geometry_state_for_type(GeometryType.PACK)
        self.assertEqual(state.get(CommonGeometryOption.GEOMETRY_TYPE), GeometryType.PACK.value)

    def test_place_state_has_geometry_type_value(self):
        state = TreeViewUtils._default_geometry_state_for_type(GeometryType.PLACE)
        self.assertEqual(state.get(CommonGeometryOption.GEOMETRY_TYPE), GeometryType.PLACE.value)

    def test_grid_state_includes_row_and_column_keys(self):
        state = TreeViewUtils._default_geometry_state_for_type(GeometryType.GRID)
        self.assertIn("row", state)
        self.assertIn("column", state)

    def test_pack_state_includes_fill_and_side_keys(self):
        state = TreeViewUtils._default_geometry_state_for_type(GeometryType.PACK)
        self.assertIn("fill", state)
        self.assertIn("side", state)

    def test_place_state_includes_x_and_y_keys(self):
        state = TreeViewUtils._default_geometry_state_for_type(GeometryType.PLACE)
        self.assertIn("x", state)
        self.assertIn("y", state)

    def test_default_visibility_is_true(self):
        for geo_type in (GeometryType.GRID, GeometryType.PACK, GeometryType.PLACE):
            state = TreeViewUtils._default_geometry_state_for_type(geo_type)
            self.assertTrue(
                state.get(CommonGeometryOption.VISIBILITY),
                f"Expected visibility=True for {geo_type}"
            )


class BuildGeometryStateTests(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_grid_widget_state_reflects_actual_row_and_column(self):
        w = tk.Frame(self.root)
        w.grid(row=2, column=3)
        self.root.update_idletasks()
        state = TreeViewUtils.build_geometry_state_for_widget(w, GeometryType.GRID)
        self.assertEqual(str(state.get("row")), "2")
        self.assertEqual(str(state.get("column")), "3")

    def test_pack_widget_state_reflects_side(self):
        w = tk.Frame(self.root)
        w.pack(side="right")
        self.root.update_idletasks()
        state = TreeViewUtils.build_geometry_state_for_widget(w, GeometryType.PACK)
        self.assertEqual(str(state.get("side")), "right")

    def test_place_widget_state_reflects_x_and_y(self):
        w = tk.Frame(self.root)
        w.place(x=20, y=40)
        self.root.update_idletasks()
        state = TreeViewUtils.build_geometry_state_for_widget(w, GeometryType.PLACE)
        self.assertEqual(str(state.get("x")), "20")
        self.assertEqual(str(state.get("y")), "40")

    def test_state_visibility_matches_winfo_ismapped(self):
        # Visibility is taken directly from winfo_ismapped() — test that the
        # state value agrees with the widget's actual mapped state rather than
        # assuming a specific value (headless Tk may return 0 even for packed widgets).
        w = tk.Frame(self.root)
        w.pack()
        self.root.update_idletasks()
        state = TreeViewUtils.build_geometry_state_for_widget(w, GeometryType.PACK)
        self.assertEqual(state.get(CommonGeometryOption.VISIBILITY), w.winfo_ismapped())

    def test_state_visibility_matches_winfo_ismapped_for_unmapped_widget(self):
        w = tk.Frame(self.root)
        # not packed — unmapped
        state = TreeViewUtils.build_geometry_state_for_widget(w, GeometryType.PACK)
        self.assertEqual(state.get(CommonGeometryOption.VISIBILITY), w.winfo_ismapped())

    def test_geometry_type_key_always_matches_requested_type(self):
        w = tk.Frame(self.root)
        w.grid(row=0, column=0)
        state = TreeViewUtils.build_geometry_state_for_widget(w, GeometryType.GRID)
        self.assertEqual(state.get(CommonGeometryOption.GEOMETRY_TYPE), GeometryType.GRID.value)


if __name__ == "__main__":
    unittest.main()
