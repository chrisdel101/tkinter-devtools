I reviewed the seven modified files in full, plus the code they call. Git was blocked, so I couldn't see the exact diff. Your rename to `_private` methods landed while I was reviewing, and I re-checked everything against the new names. All 155 tests pass. I didn't touch any of your files.

I confirmed each finding below by running the real code with the app frame as master. The scripts are in `/private/tmp/claude-501/-Users-chrisdielschnieder-code-work-python-tk-devtools/c8f3ac59-a7a9-4563-8e67-ecbae8632471/scratchpad/repro.py`.

### Bugs

1. **Closing the devtools window leaves the orange border on the app, and the event handlers stay bound.** The four border frames are created in the app's toplevel ([TreeViewHighlighter.py:92](devtools/components/widgets/treeview/TreeViewHighlighter.py#L92)). The `bind_all` calls and the `<Configure>` binding ([TreeView.py:36-39](devtools/components/widgets/treeview/TreeView.py#L36-L39)) are never removed. After `dw.destroy()`, all four frames were still on screen and `bind_all("<Map>")` was still set. The store also keeps references to every app widget.

2. **`self.master = master` in [TreeView.py:20](devtools/components/widgets/treeview/TreeView.py#L20) makes the tree count as an app widget.** `_is_devtools_widget` walks `.master` up to the app instead of the devtools window, so it misses the tree. `_is_relevant_tree_event_widget` then finds the app and says yes. Hiding and re-showing the devtools window caused 2 full rebuilds, both triggered by `...!leftwindowframe.!treeview`. A rebuild takes 0.3–0.6s on an app with 500–2000 widgets. Storing it as `self._app` instead would fix this.

3. **Selecting an unmapped or zero-size widget shows the highlight's values in the Options list.** `apply_highlight` ([TreeView.py:318](devtools/components/widgets/treeview/TreeView.py#L318)) runs before the options are read. Its fallback writes `highlightthickness=2` and `#FF4500` into the widget. For an unmapped Frame the list showed `highlightthickness: 2` and `highlightbackground: #FF4500`. The real values are `0` and `systemWindowBackgroundColor`.

4. **The error display in `handle_tree_select` never runs** ([TreeView.py:327-335](devtools/components/widgets/treeview/TreeView.py#L327-L335)). The `stuff_*` methods are wrapped in `class_fn_try_except_catcher`, which swallows exceptions, and errors that aren't Tcl errors don't even show the Alert. With a forced `ValueError`, the Options list had 0 rows, with no error row and no alert. `raise e` at [line 299](devtools/components/widgets/treeview/TreeView.py#L299) is swallowed the same way.

5. **`skip_runtime_checks` is ignored.** [DevtoolsWindow.py:33](devtools/DevtoolsWindow.py#L33) always runs the checks, even though [README.md:93](README.md#L93) documents the option. With `skip_runtime_checks=True`, `runtime_checks` was still called once.

6. **Devtools changes the host app's global settings:**
   - [style.py:12-16](devtools/style.py#L12-L16) styles `"Treeview"` instead of `"My.Treeview"`. The app's own Treeview selected colour changed from `systemSelectedTextBackgroundColor` to `grey`.
   - [DevtoolsWindow.py:37](devtools/DevtoolsWindow.py#L37) with [logging_utils.py:31-40](devtools/logging_utils.py#L31-L40) changes the app's root logger. Its level went from 30 to 8 (TRACE) and it gained a handler. An app that already called `basicConfig` prints every log line twice.

7. **Memory leak.** `tree_store_widget_by_obj_mem_id` ([TreeView.py:141-146](devtools/components/widgets/treeview/TreeView.py#L141-L146)) is written on every insert but never read or cleared. After 3 add/remove cycles it went from 5 to 8 entries while the live store stayed at 5. `tree_highlight_resize_job` ([store.py:64](devtools/components/store.py#L64)) is never used either.

### Tests

- [treeview_test.py:177](tests/treeview_test.py#L177): `unittest.main()` sits in the middle of the file. Running the file directly runs only 9 of its tests.
- [treeview_test.py:95](tests/treeview_test.py#L95) mocks `rebuild_tree_from_root`, which doesn't exist. After your rename it should be `_rebuild_tree_from_master_root`.
- [treeview_test.py:342](tests/treeview_test.py#L342) (`if not entry: return`) and [line 349](tests/treeview_test.py#L349) (`if sel:`) let the test pass without asserting anything.
- `TclEventEmitTests` repeats the tests at [lines 103-126](tests/treeview_test.py#L103-L126).
- The fixture uses `root` as master ([line 222](tests/treeview_test.py#L222)), not the app-frame setup you actually use.

### Docs and scripts

- In the README Quick Start ([README.md:78-82](README.md#L78-L82)), `title=` should be `devtools_title=`; the wrong name is silently dropped, so the window gets no title. It also passes `root` instead of the app. Lines 42 and 46 contain your local absolute paths.
- [main.py:11-12](main.py#L11-L12) points `sys.path` at a hard-coded path into your arcgis project, so it fails on any other machine. The comment at lines 65-67 contradicts the `app.pack` on line 63. `log_window` and `TestApp` are unused.

### Minor

- `on_toplevel_configure` fires for every widget's Configure event in the app, not just the toplevel. One resize of a 5-widget app caused 13 calls. It doesn't loop when idle (0 calls in 2s).
- The fallback branches in `_tree_order_key` ([TreeView.py:193-215](devtools/components/widgets/treeview/TreeView.py#L193-L215)) only run on a `TclError`, because only mapped children are sorted.
- `_get_widget_by_obj_mem_id` ([line 171](devtools/components/widgets/treeview/TreeView.py#L171)) raises `AttributeError` on a missing id, which the decorator swallows, so it returns `None`.
- In [constants.py:169-175](devtools/constants.py#L169-L175), the `TreeState` TypedDict has default values, and its keys don't match the integer keys the store actually uses.
- In [maps.py](devtools/maps.py), `PADX` (lines 10/14) and `BD` (213/214) are each listed twice. Pack `ANCHOR` is typed `BOOLEAN` ([line 40](devtools/maps.py#L40)), which has no effect right now.

I also checked whether rebuilding gets badly slower on large apps because of how the stores are copied on each insert. It doesn't (0.6s vs 0.54s at 2000 widgets), so I left it out.
