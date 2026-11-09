import tkinter as tk
import unittest
from unittest.mock import patch

from devtools.components.widgets.treeview.TreeViewUtils import TreeViewUtils
from devtools.constants import GeometryType


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
        # target is the only packed child - it must not count as its own sibling
        geo = TreeViewUtils.check_sibling_geometry_type(target)
        self.assertIsNone(geo)


class InferGeometryOptionsTests(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_pack_inference_returns_before_next_sibling(self):
        parent = tk.Frame(self.root)
        parent.pack()
        # target is created first, so the packed sibling comes after it
        target = tk.Frame(parent)
        next_sib = tk.Frame(parent)
        next_sib.pack()
        # the hidden test root reports every widget as unmapped - report them as shown
        with patch.object(tk.Frame, "winfo_ismapped", return_value=1):
            result = TreeViewUtils.infer_geometry_options(target, GeometryType.PACK)
        self.assertEqual(result, {"before": next_sib})

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

    # re-shown placed widget gets no guessed x/y - only pack and grid guess
    def test_place_inference_returns_empty_dict(self):
        parent = tk.Frame(self.root)
        parent.pack()
        target = tk.Frame(parent)
        result = TreeViewUtils.infer_geometry_options(target, GeometryType.PLACE)
        self.assertEqual(result, {})

    def test_no_parent_returns_empty_dict(self):
        target = tk.Frame.__new__(tk.Frame)
        target.master = None
        result = TreeViewUtils.infer_geometry_options(target, GeometryType.GRID)
        self.assertEqual(result, {})
