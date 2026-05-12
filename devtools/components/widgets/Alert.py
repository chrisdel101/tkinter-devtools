from __future__ import annotations
import tkinter as tk


class Alert(tk.Label):
    def __init__(self, parent, style: dict):
        self._auto_clear_ms = style.get('auto_clear_ms', 4000)
        self._after_id = None
        label_style = {k: v for k, v in style.items() if k != 'auto_clear_ms'}
        super().__init__(parent, **label_style)

    def error(self, message: str):
        if self._after_id:
            self.after_cancel(self._after_id)
        self.config(text=message)
        self.pack(fill='x')
        self._after_id = self.after(self._auto_clear_ms, self._clear)

    def _clear(self):
        self._after_id = None
        self.pack_forget()
