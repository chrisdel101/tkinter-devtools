"""
Tests for Store — state management, property setters, observer notifications.
"""
import logging
import unittest
from unittest.mock import patch

from devtools.DevtoolsWindow import DevtoolsWindowKwargs
from devtools.components.observable import Action, Observable
from devtools.components.store import Store
from devtools.constants import (
    ActionType,
    ListboxPageTemplateEnum,
    ListboxTemplateNotifyStateKey,
    TreeStateKey,
)

TEST_SETTINGS: DevtoolsWindowKwargs = {
    "show_unmapped_widgets": True,
    "devtools_title": "Test",
    "skip_runtime_checks": True,
}


class _RecordingObserver:
    def __init__(self):
        self.actions: list[Action] = []

    def notify(self, action: Action):
        self.actions.append(action)

    def actions_of_type(self, action_type: ActionType):
        return [a for a in self.actions if a.type == action_type]


class StoreInitTests(unittest.TestCase):
    def setUp(self):
        self.trace_patcher = patch.object(logging, "trace", create=True)
        self.trace_patcher.start()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_SETTINGS)

    def tearDown(self):
        self.trace_patcher.stop()

    def test_block_active_adding_defaults_false(self):
        self.assertFalse(self.store.block_active_adding)

    def test_tree_refresh_job_defaults_none(self):
        self.assertIsNone(self.store.tree_refresh_job)

    def test_tree_rebuild_in_progress_defaults_false(self):
        self.assertFalse(self.store.tree_rebuild_in_progress)

    def test_tree_rebuild_requested_defaults_false(self):
        self.assertFalse(self.store.tree_rebuild_requested)

    def test_show_unmapped_widgets_respected_from_kwargs(self):
        self.assertTrue(self.store.show_unmapped_widgets)

    def test_show_unmapped_widgets_false_when_passed_false(self):
        obs = Observable()
        s = Store(observable=obs, show_unmapped_widgets=False, **{
            "devtools_title": "T",
            "skip_runtime_checks": True,
        })
        self.assertFalse(s.show_unmapped_widgets)

    def test_tree_state_initialised_with_correct_keys(self):
        val = self.store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET)
        self.assertIsNone(val)
        ids = self.store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT)
        self.assertEqual(ids, {})
        mem = self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID)
        self.assertEqual(mem, {})

    def test_listbox_internal_state_has_options_and_geometry_keys(self):
        self.assertIn(ListboxPageTemplateEnum.OPTIONS,
                      self.store.current_listbox_template_internal_state)
        self.assertIn(ListboxPageTemplateEnum.GEOMETRY,
                      self.store.current_listbox_template_internal_state)


class StoreTreeStateTests(unittest.TestCase):
    def setUp(self):
        self.trace_patcher = patch.object(logging, "trace", create=True)
        self.trace_patcher.start()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_SETTINGS)

    def tearDown(self):
        self.trace_patcher.stop()

    def test_tree_state_set_and_get_roundtrip(self):
        sentinel = object()
        self.store.tree_state_set(TreeStateKey.SELECTED_ITEM_WIDGET, sentinel)
        self.assertIs(self.store.tree_state_get(TreeStateKey.SELECTED_ITEM_WIDGET), sentinel)

    def test_tree_state_dict_set_and_get_roundtrip(self):
        data = {"I001": object()}
        self.store.tree_state_set(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT, data)
        self.assertEqual(
            self.store.tree_state_get(TreeStateKey.WIDGETS_BY_TREE_INSERT_ID_DICT), data
        )

    def test_tree_state_mem_id_set_and_get_roundtrip(self):
        data = {42: {"tree_id": "I001"}}
        self.store.tree_state_set(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID, data)
        self.assertEqual(
            self.store.tree_state_get(TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID), data
        )


class StorePropertyNotificationsTests(unittest.TestCase):
    def setUp(self):
        self.trace_patcher = patch.object(logging, "trace", create=True)
        self.trace_patcher.start()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_SETTINGS)
        self.observer = _RecordingObserver()
        self.observable.register_observer(self.observer)

    def tearDown(self):
        self.trace_patcher.stop()

    def test_show_geometry_button_true_notifies_toggle(self):
        self.store.show_geometry_button = True
        actions = self.observer.actions_of_type(ActionType.TOGGLE_GEO_BUTTON_VISIBLE)
        self.assertTrue(any(a.data is True for a in actions))

    def test_show_geometry_button_false_notifies_toggle(self):
        self.store.show_geometry_button = False
        actions = self.observer.actions_of_type(ActionType.TOGGLE_GEO_BUTTON_VISIBLE)
        self.assertTrue(any(a.data is False for a in actions))

    def test_row_shift_true_notifies_toggle(self):
        self.store.row_shift = True
        actions = self.observer.actions_of_type(ActionType.TOGGLE_ROW_SHIFT)
        self.assertTrue(any(a.data is True for a in actions))

    def test_row_shift_false_notifies_toggle(self):
        self.store.row_shift = False
        actions = self.observer.actions_of_type(ActionType.TOGGLE_ROW_SHIFT)
        self.assertTrue(any(a.data is False for a in actions))


class StoreListboxStateTests(unittest.TestCase):
    def setUp(self):
        self.trace_patcher = patch.object(logging, "trace", create=True)
        self.trace_patcher.start()
        import tkinter as tk
        from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager
        self.root = tk.Tk()
        self.root.withdraw()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_SETTINGS)
        self.parent = tk.Frame(self.root)
        self.parent.pack()
        self.options_lb = ConfigListboxManager(
            master=self.parent,
            listbox_page_template_enum=ListboxPageTemplateEnum.OPTIONS,
            observable=self.observable,
            store=self.store,
        )
        self.geometry_lb = ConfigListboxManager(
            master=self.parent,
            listbox_page_template_enum=ListboxPageTemplateEnum.GEOMETRY,
            observable=self.observable,
            store=self.store,
        )
        self.store.listbox_templates = {
            ListboxPageTemplateEnum.OPTIONS: self.options_lb,
            ListboxPageTemplateEnum.GEOMETRY: self.geometry_lb,
        }
        self.store.current_listbox_template = self.options_lb

    def tearDown(self):
        self.root.destroy()
        self.trace_patcher.stop()

    def test_listbox_value_state_set_and_get_roundtrip(self):
        self.store.listbox_manager_template_value_state_set(
            ListboxTemplateNotifyStateKey.SELECTED_INDEX, 3
        )
        result = self.store.listbox_manager_template_value_state_get(
            ListboxTemplateNotifyStateKey.SELECTED_INDEX
        )
        self.assertEqual(result, 3)

    def test_listbox_value_state_set_with_override(self):
        self.store.listbox_manager_template_value_state_set(
            ListboxTemplateNotifyStateKey.SELECTED_INDEX,
            7,
            page_insert_override=ListboxPageTemplateEnum.GEOMETRY,
        )
        result = self.store.listbox_manager_template_value_state_get(
            ListboxTemplateNotifyStateKey.SELECTED_INDEX,
            page_insert_override=ListboxPageTemplateEnum.GEOMETRY,
        )
        self.assertEqual(result, 7)

    def test_listbox_values_state_set_notifies_insert_action(self):
        observer = _RecordingObserver()
        self.observable.register_observer(observer)
        self.store.listbox_manager_template_values_state_set(
            {"relief": "flat"}, page_insert_override=ListboxPageTemplateEnum.OPTIONS
        )
        actions = observer.actions_of_type(ActionType.INSERT_LISTBOX_ITEMS)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].data, {"relief": "flat"})

    def test_listbox_values_state_set_stores_current_values(self):
        self.store.listbox_manager_template_values_state_set(
            {"text": "hello"}, page_insert_override=ListboxPageTemplateEnum.OPTIONS
        )
        stored = self.store.current_listbox_template_internal_state[
            ListboxPageTemplateEnum.OPTIONS
        ]["current_values_state"]
        self.assertEqual(stored, {"text": "hello"})

    def test_add_and_remove_existing_store_wrappers(self):
        import tkinter as tk
        w = tk.Frame(self.parent)
        self.store.add_existing_store_wrapper(w)
        self.assertIn(w, self.store.existing_combobox_wrappers)
        self.store.remove_existing_store_wrappers()
        self.assertEqual(self.store.existing_combobox_wrappers, [])


class StoreHiddenWidgetTests(unittest.TestCase):
    def setUp(self):
        self.trace_patcher = patch.object(logging, "trace", create=True)
        self.trace_patcher.start()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_SETTINGS)

    def tearDown(self):
        self.trace_patcher.stop()

    def test_hidden_widgets_initialises_empty(self):
        self.assertEqual(self.store.hidden_widgets, {})

    def test_hidden_widgets_can_be_set_and_retrieved(self):
        sentinel = {1: "x"}
        self.store.hidden_widgets = sentinel
        self.assertEqual(self.store.hidden_widgets, sentinel)


if __name__ == "__main__":
    unittest.main()
