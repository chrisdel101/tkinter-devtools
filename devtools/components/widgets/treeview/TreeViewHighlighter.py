from __future__ import annotations
import tkinter as tk
from devtools.decorators.decorators import class_fn_try_except_catcher
from devtools.style import Style


class TreeViewHighlighter:

    @class_fn_try_except_catcher
    # Draws the highlight around the widget selected in the tree.
    def __init__(self, tree: tk.Misc, observable, store):
        self._tree = tree
        self._observable = observable
        self._store = store

    @class_fn_try_except_catcher
    # Highlight the selected widget using an overlay frame or a direct config fallback.
    def apply_highlight(self, widget: tk.Widget):
        self._store.is_tree_applying_highlight = True
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
                widget.configure(
                    highlightbackground=Style.treeview['highlightbackground'],
                    highlightthickness=Style.treeview['highlightthickness'],
                )
                self._store.tree_highlighted_widget = widget
        except tk.TclError:
            self._store.tree_highlight_saved_config = None
        # Clear flag after_idle so queued Tk events from configure fire while flag is still True
        self._tree.after_idle(self._clear_applying_highlight)

    @class_fn_try_except_catcher
    # Remove the highlight from the previously highlighted widget.
    def _remove_highlight(self):
        if self._store.tree_highlighted_widget and self._store.tree_highlight_saved_config:
            try:
                strategy = self._store.tree_highlight_saved_config.get('strategy')
                if strategy == 'config':
                    self._store.tree_highlighted_widget.configure(**self._store.tree_highlight_saved_config.get('config', {}))
            except tk.TclError:
                pass
        self._hide_highlight_overlay()
        self._store.tree_highlighted_widget = None
        self._store.tree_highlight_saved_config = None

    @class_fn_try_except_catcher
    # Place four thin Frame edges around the widget to draw a highlight border overlay.
    def _show_highlight_overlay(self, widget: tk.Widget) -> bool:
        if not widget.winfo_exists():
            return False
        overlay_parent = widget.winfo_toplevel()
        if overlay_parent is None:
            return False

        widget.update_idletasks()
        if widget.winfo_width() <= 1 or widget.winfo_height() <= 1:
            return False

        if (
            len(self._store.tree_highlight_overlay_edges) != 4
            or any(not edge.winfo_exists() for edge in self._store.tree_highlight_overlay_edges)
            or self._store.tree_highlight_overlay_parent is not overlay_parent
        ):
            self._hide_highlight_overlay()
            self._store.tree_highlight_overlay_parent = overlay_parent
            self._store.tree_highlight_overlay_edges = [
                tk.Frame(overlay_parent, bg=Style.treeview['highlightbackground'], bd=0, highlightthickness=0)
                for _ in range(4)
            ]

        border_size = Style.treeview['highlightthickness']
        top_edge, right_edge, bottom_edge, left_edge = self._store.tree_highlight_overlay_edges

        # in_=widget - Tk keeps the edges on the widget when it moves or resizes, and hides them when it unmaps
        top_edge.place(in_=widget, bordermode="outside", x=0, y=0, relwidth=1, height=border_size)
        right_edge.place(in_=widget, bordermode="outside", relx=1, x=-border_size, y=0, width=border_size, relheight=1)
        bottom_edge.place(in_=widget, bordermode="outside", x=0, rely=1, y=-border_size, relwidth=1, height=border_size)
        left_edge.place(in_=widget, bordermode="outside", x=0, y=0, width=border_size, relheight=1)

        # Raise edges to the top of the toplevel's stacking order so nothing covers them.
        for edge in self._store.tree_highlight_overlay_edges:
            edge.lift()
        # Repaint once idle - otherwise some sides don't draw on open or when devtools is focused
        self._tree.after_idle(self._repaint_highlight_overlay)
        return True

    @class_fn_try_except_catcher
    # Force each edge to redraw by re-setting its background.
    def _repaint_highlight_overlay(self):
        for edge in self._store.tree_highlight_overlay_edges:
            if edge.winfo_exists():
                edge.configure(bg=edge.cget('bg'))

    @class_fn_try_except_catcher
    # Hide all overlay edge frames by removing them from the layout.
    def _hide_highlight_overlay(self):
        for edge in self._store.tree_highlight_overlay_edges:
            if edge.winfo_exists():
                edge.place_forget()

    @class_fn_try_except_catcher
    # Restore the highlighted widget and destroy the edges - they live in the app toplevel so closing devtools leaves them
    def destroy_highlight_overlay(self):
        self._remove_highlight()
        for edge in self._store.tree_highlight_overlay_edges:
            if edge.winfo_exists():
                edge.destroy()
        self._store.tree_highlight_overlay_edges = []
        self._store.tree_highlight_overlay_parent = None

    @class_fn_try_except_catcher
    # Clear the applying-highlight guard flag after queued Tk events have been processed.
    def _clear_applying_highlight(self):
        self._store.is_tree_applying_highlight = False
