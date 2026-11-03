import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from devtools.DevtoolsWindow import DevtoolsWindowKwargs
from devtools.components.observable import Action
from devtools.components.observable import Observable
from devtools.components.store import Store
from devtools.components.widgets.config_listbox.ConfigListboxManager import ConfigListboxManager
from devtools.components.widgets.windows.RightWindowFrame import RightWindowFrame
from devtools.constants import ActionType, CommonGeometryOption, ListBoxEntryInputAction, ListboxItemState, ListboxPageTemplateEnum, PackGeometryOptionName, TreeStateKey


class RecordingObserver:
    def __init__(self):
        self.actions = []

    def notify(self, action):
        self.actions.append(action)


TEST_RUNTIME_SETTINGS: DevtoolsWindowKwargs = {
    "show_unmapped_widgets": True,
    "devtools_title": "Devtools Test",
    "skip_runtime_checks": True,
}


class ConfigListboxManagerTests(unittest.TestCase):
    def setUp(self):

        self.root = tk.Tk()
        self.root.withdraw()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_RUNTIME_SETTINGS)
        self.parent = tk.Frame(self.root)
        self.parent.pack()
        self.listbox = ConfigListboxManager(
            master=self.parent,
            listbox_page_template_enum=ListboxPageTemplateEnum.OPTIONS,
            observable=self.observable,
            store=self.store,
        )
        self.store.current_listbox_template = self.listbox
        self.store.listbox_templates = {ListboxPageTemplateEnum.OPTIONS: self.listbox}
        self.recording_observer = RecordingObserver()
        self.observable.register_observer(self.recording_observer)

    def tearDown(self):
        # Run already-queued callbacks while the widgets still exist
        self.root.update_idletasks()
        self.root.destroy()

    def test_insert_listbox_items_normalizes_bool_display_values(self):
        self.listbox.insert_listbox_items(
            **{
                CommonGeometryOption.VISIBILITY: True,
                PackGeometryOptionName.EXPAND: False,
            }
        )

        self.assertEqual(self.listbox.get(0), "visibility: true")
        self.assertEqual(self.listbox.get(1), "expand: false")

    def test_init_sets_name_and_registers_observer(self):
        self.assertEqual(self.listbox.name, "OPTIONS listbox")
        self.assertEqual(self.listbox._listbox_page_template_insert_enum, ListboxPageTemplateEnum.OPTIONS)
        self.assertIn(self.listbox, self.observable._observers)

    def test_delete_all_listbox_items_clears_entries(self):
        self.listbox.insert(tk.END, "alpha: 1")
        self.listbox.insert(tk.END, "beta: 2")

        self.listbox.delete_all_listbox_items()

        self.assertEqual(self.listbox.size(), 0)

    def test_listbox_key_focus_out_ignores_create_handoff_when_value_editor_exists(self):
        self.store.listbox_entry_input_action = ListBoxEntryInputAction.CREATE
        self.store.block_active_adding = True
        self.listbox.value_box_wrapper = tk.Frame(self.parent)

        self.listbox.listbox_key_focus_out(None, tk.Frame(self.parent))

        self.assertEqual(self.recording_observer.actions, [])
        self.assertTrue(self.store.block_active_adding)
        self.assertEqual(self.store.listbox_entry_input_action, ListBoxEntryInputAction.CREATE)

    def test_listbox_key_focus_out_notifies_subtract_when_editing_stops(self):
        key_wrapper = tk.Frame(self.parent)
        self.store.listbox_entry_input_action = ListBoxEntryInputAction.UPDATE
        self.store.block_active_adding = True

        self.listbox.listbox_key_focus_out(None, key_wrapper)

        self.assertFalse(self.store.block_active_adding)
        self.assertIsNone(self.store.listbox_entry_input_action)
        self.assertTrue(any(action.type == ActionType.HANDLE_SUBTRACT_INDEX for action in self.recording_observer.actions))
        self.assertFalse(key_wrapper.winfo_exists())

    def test_listbox_value_focus_out_create_mode_notifies_and_resets_state(self):
        value_wrapper = tk.Frame(self.parent)
        self.store.existing_combobox_wrappers = [value_wrapper]
        self.store.listbox_entry_input_action = ListBoxEntryInputAction.CREATE
        self.store.block_active_adding = True
        self.store.allow_input_focus_out_logic = False
        event = SimpleNamespace(widget=value_wrapper)

        self.listbox.listbox_value_focus_out(event, *self.store.existing_combobox_wrappers)

        self.assertFalse(self.store.block_active_adding)
        self.assertTrue(self.store.allow_input_focus_out_logic)
        self.assertIsNone(self.store.listbox_entry_input_action)
        self.assertTrue(any(action.type == ActionType.HANDLE_SUBTRACT_INDEX for action in self.recording_observer.actions))
        self.assertFalse(value_wrapper.winfo_exists())

    def test_start_update_routes_option_row_to_update_handler(self):
        self.listbox.insert(tk.END, "relief: flat")
        event = SimpleNamespace(x=0, y=0)

        with patch.object(self.listbox, "_get_index_from_event_coords", return_value=0), \
             patch.object(self.listbox, "handle_entry_input_update") as update_handler:
            self.listbox.start_update(event)

        self.assertTrue(update_handler.called)
        kwargs = update_handler.call_args.kwargs
        self.assertEqual(kwargs["index"], 0)
        self.assertEqual(kwargs["listbox_item_pairs_dict"]["key"], "relief")
        self.assertEqual(kwargs["listbox_item_pairs_dict"]["value"], "flat")
        self.assertIsInstance(kwargs["config_setting_map"], dict)
        self.assertIn("type", kwargs["config_setting_map"])

    def test_start_update_returns_break_for_read_only_item(self):
        self.listbox.insert(tk.END, "relief: flat")
        event = SimpleNamespace(x=0, y=0)

        with patch.object(self.listbox, "_get_index_from_event_coords", return_value=0), \
             patch.object(self.listbox, "check_maps_for_state", return_value=ListboxItemState.READ_ONLY), \
             patch.object(self.listbox, "handle_entry_input_update") as update_handler:
            result = self.listbox.start_update(event)

        self.assertEqual(result, "break")
        update_handler.assert_not_called()

    def test_submit_option_update_emits_update_action(self):
        self.store.existing_combobox_wrappers = []
        value_widget = SimpleNamespace(get=lambda: "raised")

        self.listbox.insert_value_output_and_apply_to_page(
            value_entry_widget=value_widget,
            key_entry_value="relief",
            updated_option_value="raised",
            event=None,
        )

        self.assertTrue(
            any(
                action.type == ActionType.UPDATE_TREE_ITEM_TO_PAGE_WIDGET_OPTION_CONFIG
                and action.data == {"key": "relief", "value": "raised"}
                for action in self.recording_observer.actions
            )
        )

    def test_handle_build_value_combobox_box_from_key_combo_box_places_and_focuses(self):
        combo = SimpleNamespace(pack=lambda **_: None, focus_set=lambda: None)

        def _build_combo_box(*args, **kwargs):
            self.listbox.value_box_wrapper = tk.Frame(self.parent)
            return combo

        with patch.object(self.listbox, "build_value_combo_box", side_effect=_build_combo_box), \
             patch.object(self.listbox, "_set_selected_by_index") as set_selected:
            self.listbox.handle_build_value_combobox_box_from_key_combo_box(
                index=2,
                value_inside=tk.StringVar(value="relief"),
                item_option_vals_list=["flat", "raised"],
            )

        self.assertIn(self.listbox.value_box_wrapper, self.store.existing_combobox_wrappers)
        set_selected.assert_called_once_with(2)

    def test_handle_build_value_entry_from_key_entry_uses_spinbox_for_numeric_types(self):
        fake_spinbox = SimpleNamespace(pack=lambda **_: None, focus_set=lambda: None)

        with patch.object(self.listbox, "build_value_spin_box", return_value=fake_spinbox):
            self.listbox.handle_build_value_entry_from_key_entry(
                index=1,
                key_entry_widget=SimpleNamespace(),
                key_entry_value="padx",
                y_coord=0,
                current_option_val="3",
                config_setting_map={"type": int},
            )

        self.assertIsNotNone(self.listbox.spin_box_wrapper)
        self.assertIn(self.listbox.spin_box_wrapper, self.store.existing_combobox_wrappers)

    def test_handle_build_value_entry_from_key_entry_builds_plain_entry_when_no_mapping(self):
        with patch.object(self.listbox, "_set_selected_by_index") as set_selected:
            self.listbox.handle_build_value_entry_from_key_entry(
                index=4,
                key_entry_widget=SimpleNamespace(),
                key_entry_value="text",
                y_coord=0,
                current_option_val=None,
                config_setting_map={"type": str},
            )

        self.assertIsNotNone(self.listbox.value_box_wrapper)
        self.assertIn(self.listbox.value_box_wrapper, self.store.existing_combobox_wrappers)
        set_selected.assert_called_once_with(4)

    def test_handle_entry_input_update_routes_to_plain_entry_path_when_no_values_map(self):
        self.listbox.insert(tk.END, "relief: flat")
        self.root.update_idletasks()

        with patch.object(self.listbox, "handle_build_value_entry_from_key_entry") as plain_entry_builder:
            self.listbox.handle_entry_input_update(
                index=0,
                config_setting_map={"type": str, "values": None},
                listbox_item_pairs_dict={"key": "relief", "value": "flat"},
            )

        plain_entry_builder.assert_called_once()

    def test_handle_entry_input_create_builds_key_combobox_for_current_template_state(self):
        self.store.current_listbox_template_internal_state[ListboxPageTemplateEnum.OPTIONS][
            "current_values_state"
        ] = {"relief": "flat", "text": "hello"}

        fake_key_combo = SimpleNamespace(pack=lambda **_: None, focus_set=lambda: None)

        def _build_key_combo_box(*args, **kwargs):
            self.listbox.key_box_wrapper = tk.Frame(self.parent)
            return fake_key_combo

        with patch.object(self.listbox, "build_key_combo_box", side_effect=_build_key_combo_box), \
             patch.object(self.listbox, "_set_selected_by_index") as set_selected:
            self.listbox.handle_entry_input_create(index=3)

        self.assertEqual(self.store.listbox_entry_input_action, ListBoxEntryInputAction.CREATE)
        self.assertIn(self.listbox.key_box_wrapper, self.store.existing_combobox_wrappers)
        set_selected.assert_called_once_with(3)

    def test_notify_dispatches_action_via_utils(self):
        action = Action(type=ActionType.DELETE_ALL_LISTBOX_ITEMS)
        with patch("devtools.components.widgets.config_listbox.ConfigListboxManager.Utils.dispatch_action") as dispatch:
            self.listbox.notify(action)
        dispatch.assert_called_once_with(self.listbox, action)


class RightWindowAddFlowTests(unittest.TestCase):
    class _FakeListboxTemplate:
        def __init__(self, selection=()):
            self._selection = selection
            self.insert_calls = []
            self.create_calls = []

        def curselection(self):
            return self._selection

        def insert_listbox_item(self, index, value):
            self.insert_calls.append((index, value))

        def handle_entry_input_create(self, index):
            self.create_calls.append(index)

    def _build_right_window_for_handle_add(self, fake_listbox, blocked=False):
        right_window = RightWindowFrame.__new__(RightWindowFrame)
        right_window._store = SimpleNamespace(
            block_active_adding=blocked,
            current_listbox_template=fake_listbox,
        )
        return right_window

    def test_handle_add_inserts_at_top_when_nothing_selected(self):
        fake_listbox = self._FakeListboxTemplate(selection=())
        right_window = self._build_right_window_for_handle_add(fake_listbox, blocked=False)

        right_window.handle_add()

        self.assertTrue(right_window._store.block_active_adding)
        self.assertEqual(fake_listbox.insert_calls, [(0, "")])
        self.assertEqual(fake_listbox.create_calls, [0])

    def test_handle_add_inserts_after_selected_row(self):
        fake_listbox = self._FakeListboxTemplate(selection=(3,))
        right_window = self._build_right_window_for_handle_add(fake_listbox, blocked=False)

        right_window.handle_add()

        self.assertEqual(fake_listbox.insert_calls, [(4, "")])
        self.assertEqual(fake_listbox.create_calls, [4])

    def test_handle_add_noops_when_add_is_blocked(self):
        fake_listbox = self._FakeListboxTemplate(selection=(1,))
        right_window = self._build_right_window_for_handle_add(fake_listbox, blocked=True)

        right_window.handle_add()

        self.assertEqual(fake_listbox.insert_calls, [])
        self.assertEqual(fake_listbox.create_calls, [])


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# RightWindowFrame — tab switching, row shift, geo button visibility
# ---------------------------------------------------------------------------

class RightWindowTabTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_RUNTIME_SETTINGS)
        self.parent = tk.Frame(self.root)
        self.parent.pack()
        from devtools.components.widgets.windows.RightWindowFrame import RightWindowFrame
        self.rw = RightWindowFrame(
            parent=self.parent,
            observable=self.observable,
            store=self.store,
        )

    def tearDown(self):
        self.root.destroy()

    def test_options_tab_active_by_default(self):
        from devtools.constants import ListboxPageTemplateEnum
        self.assertEqual(
            self.store.current_listbox_template._listbox_page_template_insert_enum,
            ListboxPageTemplateEnum.OPTIONS,
        )

    def test_switching_to_geometry_tab_updates_current_template(self):
        from devtools.constants import ListboxPageTemplateEnum
        self.rw.pack_listbox_page_insert(ListboxPageTemplateEnum.GEOMETRY)
        self.assertEqual(
            self.store.current_listbox_template._listbox_page_template_insert_enum,
            ListboxPageTemplateEnum.GEOMETRY,
        )

    def test_switching_to_options_tab_updates_current_template(self):
        from devtools.constants import ListboxPageTemplateEnum
        self.rw.pack_listbox_page_insert(ListboxPageTemplateEnum.GEOMETRY)
        self.rw.pack_listbox_page_insert(ListboxPageTemplateEnum.OPTIONS)
        self.assertEqual(
            self.store.current_listbox_template._listbox_page_template_insert_enum,
            ListboxPageTemplateEnum.OPTIONS,
        )

    def test_geometry_tab_sets_row_shift_false(self):
        from devtools.constants import ListboxPageTemplateEnum
        self.rw.pack_listbox_page_insert(ListboxPageTemplateEnum.GEOMETRY)
        self.assertFalse(self.store.row_shift)

    def test_options_tab_sets_row_shift_true(self):
        from devtools.constants import ListboxPageTemplateEnum
        self.rw.pack_listbox_page_insert(ListboxPageTemplateEnum.GEOMETRY)
        self.rw.pack_listbox_page_insert(ListboxPageTemplateEnum.OPTIONS)
        self.assertTrue(self.store.row_shift)
    # test that clicking the tab already open does not pack it again    
    def test_handle_pack_click_same_tab_is_noop(self):
        from devtools.constants import ListboxPageTemplateEnum
        # records calls to the pack function - a re-pack sets the same template, so only the call shows it ran
        with patch.object(self.rw, "pack_listbox_page_insert") as pack_insert:
            self.rw.handle_pack_listbox_page_insert_click(ListboxPageTemplateEnum.OPTIONS)
        pack_insert.assert_not_called()

    def test_toggle_row_shift_enables_add_subtract_buttons(self):
        self.rw.toggle_row_shift(True)
        self.assertEqual(str(self.rw.add_config_button.cget("state")), tk.NORMAL)
        self.assertEqual(str(self.rw.subtract_config_button.cget("state")), tk.NORMAL)

    def test_toggle_row_shift_disables_add_subtract_buttons(self):
        self.rw.toggle_row_shift(False)
        self.assertEqual(str(self.rw.add_config_button.cget("state")), tk.DISABLED)
        self.assertEqual(str(self.rw.subtract_config_button.cget("state")), tk.DISABLED)


class RightWindowSubtractTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_RUNTIME_SETTINGS)
        self.parent = tk.Frame(self.root)
        self.parent.pack()
        from devtools.components.widgets.windows.RightWindowFrame import RightWindowFrame
        self.rw = RightWindowFrame(
            parent=self.parent,
            observable=self.observable,
            store=self.store,
        )
        # wire a page widget with a frozen config so subtract can look it up
        self.page_widget = tk.Frame(self.root)
        self.page_widget.pack()
        self.root.update_idletasks()
        from devtools.utils import Utils
        frozen = Utils.conform_option_lisbox_config(
            Utils.filter_non_used_config_options(self.page_widget.configure())
        )
        self.store.tree_state_set(
            TreeStateKey.SELECTED_ITEM_WIDGET, self.page_widget
        )
        self.store.tree_state_set(
            TreeStateKey.MEM_WIDGET_STORE_BY_PY_MEM_ID,
            {id(self.page_widget): {
                "tree_id": "I_FAKE",
                "widget": self.page_widget,
                "widget_config_init_frozen": frozen,
            }}
        )

    def tearDown(self):
        self.root.destroy()

    def test_subtract_selection_removes_listbox_row(self):
        lb = self.store.current_listbox_template
        lb.insert(tk.END, "relief: flat")
        lb.selection_set(0)
        lb.activate(0)
        before = lb.size()
        self.rw.handle_subtract_selection()
        self.assertEqual(lb.size(), before - 1)

    def test_subtract_selection_noop_when_nothing_selected(self):
        lb = self.store.current_listbox_template
        lb.insert(tk.END, "relief: flat")
        # no selection
        before = lb.size()
        self.rw.handle_subtract_selection()
        self.assertEqual(lb.size(), before)

    def test_subtract_selection_blocked_when_add_in_progress(self):
        lb = self.store.current_listbox_template
        lb.insert(tk.END, "relief: flat")
        lb.selection_set(0)
        self.store.block_active_adding = True
        before = lb.size()
        self.rw.handle_subtract_selection()
        self.assertEqual(lb.size(), before)

    def test_handle_subtract_index_removes_row_at_index(self):
        lb = self.store.current_listbox_template
        lb.insert(tk.END, "alpha: 1")
        lb.insert(tk.END, "beta: 2")
        self.rw.handle_subtract_index(0)
        self.assertEqual(lb.size(), 1)
        self.assertEqual(lb.get(0), "beta: 2")


class RightWindowErrorTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.observable = Observable()
        self.store = Store(observable=self.observable, **TEST_RUNTIME_SETTINGS)
        self.parent = tk.Frame(self.root)
        self.parent.pack()
        from devtools.components.widgets.windows.RightWindowFrame import RightWindowFrame
        self.rw = RightWindowFrame(
            parent=self.parent,
            observable=self.observable,
            store=self.store,
        )

    def tearDown(self):
        self.root.destroy()

    def test_show_right_window_error_displays_message(self):
        self.rw.show_right_window_error("something broke")
        self.assertEqual(self.rw._alert._label.cget("text"), "something broke")

    def test_show_right_window_error_packs_alert(self):
        self.rw.show_right_window_error("oops")
        self.assertNotEqual(self.rw._alert.winfo_manager(), "")


# ---------------------------------------------------------------------------
# Alert — show / auto-clear / close
# ---------------------------------------------------------------------------

class AlertTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        from devtools.components.widgets.Alert import Alert
        self.parent = tk.Frame(self.root)
        self.parent.pack()
        self.alert = Alert(self.parent)

    def tearDown(self):
        self.root.destroy()

    def test_error_sets_label_text(self):
        self.alert.error("test error")
        self.assertEqual(self.alert._label.cget("text"), "test error")

    def test_error_packs_alert(self):
        self.alert.error("visible now")
        self.assertNotEqual(self.alert.winfo_manager(), "")

    def test_clear_hides_alert(self):
        self.alert.error("something")
        self.alert._clear()
        self.assertEqual(self.alert.winfo_manager(), "")

    def test_clear_cancels_after_id(self):
        self.alert.error("something")
        after_id = self.alert._after_id
        self.assertIsNotNone(after_id)
        self.alert._clear()
        self.assertIsNone(self.alert._after_id)

    def test_second_error_replaces_text(self):
        self.alert.error("first")
        self.alert.error("second")
        self.assertEqual(self.alert._label.cget("text"), "second")