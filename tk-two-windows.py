from tkinter import *
from tkinter import ttk
import tkinter as tk

from DevtoolsWindow import DevtoolsWindow

def open_dev_tools(main_root):
    # # main devtools window
    dev_window = DevtoolsWindow(main_root)
    dev_window.attach_tree_select()
    dev_window.build_tree(root)
    dev_window.select_tree_item(dev_window.tree.get_children()[0])  # Select the first item by default



root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Label(frm, text="Hello World2!").grid(column=0, row=1)
ttk.Button(frm, text="Quit").grid(column=1, row=0)
open_dev_tools(root)
root.mainloop()