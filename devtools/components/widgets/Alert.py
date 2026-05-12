from __future__ import annotations
import tkinter as tk
from devtools.style import Style


class Alert(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._auto_clear_ms = 4000
        self._after_id = None

        self._label = tk.Label(self, text='', **Style.right_window['error_bar'])
        self._label.pack(side='left', fill='both', expand=True)

        self._close_btn = tk.Button(self, text='✕', command=self._clear, relief='flat', bd=0)
        self._close_btn.pack(side='right')

        parent.bind('<Configure>', self._on_parent_resize, add='+')

    def _on_parent_resize(self, event):
        self._label.config(wraplength=event.width - 30)

    def error(self, message: str):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._label.config(text=message)
        self.pack(fill='x')
        self._after_id = self.after(self._auto_clear_ms, self._clear)

    def _clear(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = None
        self.pack_forget()
