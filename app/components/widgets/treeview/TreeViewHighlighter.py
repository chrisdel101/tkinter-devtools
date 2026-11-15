from __future__ import annotations
import tkinter as tk
from app.decorators.decorators import class_fn_try_except_catcher
from app.style import Style


class TreeViewHighlighter:

    @class_fn_try_except_catcher
    # Draws the highlight around the widget selected in the tree.
    def __init__(self, tree: tk.Misc, observable, store):
        self._tree = tree
        self._observable = observable
        self._store = store

    @class_fn_try_except_catcher
    # outline the selected widget with border edges so the app's own widget options are never changed
    def apply_highlight(self, widget: tk.Widget):
        self._store.is_tree_applying_highlight = True
        self._remove_highlight()
        if self._show_highlight_overlay(widget):
            self._store.tree_highlighted_widget = widget
        # Clear flag after_idle so Tk events queued by the highlight fire while flag is still True
        self._tree.after_idle(self._clear_applying_highlight)

    @class_fn_try_except_catcher
    # hide the border edges and forget the widget so a new select or devtools close starts clean
    def _remove_highlight(self):
        self._hide_highlight_overlay()
        self._store.tree_highlighted_widget = None

    @class_fn_try_except_catcher
    # Place four thin Frame edges around the widget to draw a highlight border overlay.
    def _show_highlight_overlay(self, widget: tk.Widget) -> bool:
        if not widget.winfo_exists():
            return False
        overlay_parent = widget.winfo_toplevel()
        # if no top level window do not valid to highlight
        if overlay_parent is None:
            return False

        if (
            len(self._store.tree_highlight_overlay_edges) != 4
            or any(not edge.winfo_exists() for edge in self._store.tree_highlight_overlay_edges)
            or self._store.tree_highlight_overlay_parent is not overlay_parent
        ):
            # destroy, not hide - hidden edges pile up in the old window
            self.destroy_highlight_overlay()
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
    # destroy the edges on devtools close or window switch - they live in the app's windows, so nothing else removes them
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
