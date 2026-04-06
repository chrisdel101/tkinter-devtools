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
      result = Utils.build_split_str_pairs_dict("geometry type: pack")
      self.assertEqual(result["key"], "geometry type")
      self.assertEqual(result["value"], "pack")

   def test_alias_resolvers_roundtrip_geometry_type(self):
      ui_key = Utils.listbox_option_to_type_alias_direction_alias_resolver("geometry_type")
      self.assertEqual(ui_key, "geometry type")

      internal_key = Utils.listbox_type_to_option_alias_direction_alias_resolver(ui_key)
      self.assertEqual(internal_key, "geometry_type")

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