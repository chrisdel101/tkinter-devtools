from abc import ABC
import tkinter as tk

# abstract class - do not init - inner window frames inside Toplevel window
class WindowFrame(ABC, tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
    
