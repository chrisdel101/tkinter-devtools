from __future__ import annotations
import tkinter as tk

# abstract class - do not init - inner window frames inside Toplevel window
class WindowFrame(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
    
