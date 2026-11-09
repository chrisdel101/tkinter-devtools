import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from devtools.constants import GeometryType
from devtools.geometry_info import GeometryManagerInfo
from devtools.utils import Utils


class UtilsTests(unittest.TestCase):
   def test_non_zero_falsey(self):
      self.assertTrue(Utils.non_zero_falsey(None))
      self.assertTrue(Utils.non_zero_falsey(""))
      self.assertFalse(Utils.non_zero_falsey(0))
      self.assertFalse(Utils.non_zero_falsey(1))

   def test_build_split_str_pairs_dict(self):
      result1 = Utils.build_split_str_pairs_dict("geometry type: pack")
      self.assertEqual(result1["key"], "geometry type")
      self.assertEqual(result1["value"], "pack")

      result2 = Utils.build_split_str_pairs_dict("text: http://localost3030/333?11")
      self.assertEqual(result2["key"], "text")
      self.assertEqual(result2["value"], "http://localost3030/333?11")

   def test_alias_resolvers_roundtrip_geometry_type(self):
      ui_key = Utils.listbox_option_to_type_alias_direction_alias_resolver("geometry_type")
      self.assertEqual(ui_key, "geometry type")

      internal_key = Utils.listbox_type_to_option_alias_direction_alias_resolver(ui_key)
      self.assertEqual(internal_key, "geometry_type")

   def test_patch_base_dict_overwrite(self):
      base = {'a': 1, 'b': 2}
      result = Utils.patch_base_dict(base, a=10)
      self.assertEqual(result, {'a': 10, 'b': 2})

   def test_patch_base_dict_add_new_key(self):
      base = {'a': 1}
      result = Utils.patch_base_dict(base, b=2)
      self.assertEqual(result, {'a': 1, 'b': 2})

   def test_patch_base_dict_no_overwrite_with_falsey(self):
      base = {'a': 1}
      result = Utils.patch_base_dict(base, a=None)
      self.assertEqual(result, {'a': 1})
   def test_hide_widget_pack_stores_after_anchor_when_middle_child(self):
      store = SimpleNamespace(hidden_widgets={})
      widget = MagicMock()
      prev_sibling = object()
      next_sibling = object()

      widget.master.pack_slaves.return_value = [prev_sibling, widget, next_sibling]
      geo_info = GeometryManagerInfo(GeometryType.PACK, {}, name="demo")

      with patch.object(Utils, "build_widget_geometry_manager_info", return_value=geo_info):
         Utils.hide_widget(widget, store)

      saved = store.hidden_widgets[id(widget)]
      self.assertEqual(saved.geometry_type, GeometryType.PACK)
      self.assertEqual(saved.geometry_options.get("after"), prev_sibling)
      widget.pack_forget.assert_called_once()

   def test_hide_widget_pack_stores_before_anchor_when_first_child(self):
      store = SimpleNamespace(hidden_widgets={})
      widget = MagicMock()
      next_sibling = object()

      widget.master.pack_slaves.return_value = [widget, next_sibling]
      geo_info = GeometryManagerInfo(GeometryType.PACK, {}, name="demo")

      with patch.object(Utils, "build_widget_geometry_manager_info", return_value=geo_info):
         Utils.hide_widget(widget, store)

      saved = store.hidden_widgets[id(widget)]
      self.assertEqual(saved.geometry_type, GeometryType.PACK)
      self.assertEqual(saved.geometry_options.get("before"), next_sibling)
      widget.pack_forget.assert_called_once()

   def _widget_stub(self, widget_class, is_mapped):
      widget = MagicMock()
      widget.winfo_class.return_value = widget_class
      widget.winfo_ismapped.return_value = is_mapped
      widget.winfo_width.return_value = 200
      widget.winfo_height.return_value = 100
      return widget

   def test_resolve_drawn_size_replaces_the_request_with_the_drawn_size(self):
      frame = self._widget_stub("Frame", True)
      result = Utils.resolve_drawn_size(frame, {"height": "30", "width": "40", "bg": "red"})
      self.assertEqual(result, {"height": 100, "width": 200, "bg": "red"})

   def test_resolve_drawn_size_keeps_text_unit_sizes(self):
      button = self._widget_stub("Button", True)
      result = Utils.resolve_drawn_size(button, {"height": 2, "width": 2})
      self.assertEqual(result, {"height": 2, "width": 2})

   def test_resolve_drawn_size_keeps_the_option_of_an_unmapped_widget(self):
      frame = self._widget_stub("Frame", False)
      result = Utils.resolve_drawn_size(frame, {"height": "30", "width": "40"})
      self.assertEqual(result, {"height": "30", "width": "40"})
