import tkinter as tk

class ConfigEntry(tk.Entry):
    def __init__(self, master=None, label_text="", default_value="", callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.label_text = label_text
        self.default_value = default_value
        self.callback = callback
        self.var = tk.StringVar()
        self.var.set(self.default_value)
        self.config(textvariable=self.var)
        self.var.trace_add('write', self.on_value_change)

    def on_value_change(self, *args):
        if self.callback:
            self.callback(self.label_text, self.var.get())