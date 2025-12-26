from tkinter import *
import tkinter as tk
from tkinter import ttk
from devtools.style import Style

from devtools.DevtoolsWindow import DevtoolsWindow
    
root = Tk()
style = ttk.Style()
style.configure(
    "My.Treeview",
    **Style.treeview
)
root_inner_frame = tk.Frame(root, padx=10, width=300, height=200)
tk.Label(root_inner_frame, text="Hello World!").grid(column=0, row=0)
tk.Label(root_inner_frame, text="Hello World2!").grid(column=0, row=1)
tk.Button(root_inner_frame, text="Quit").grid(column=1, row=0)
root_inner_frame.grid()
# force geometry live changes   
root_inner_frame.grid_propagate(False)
DevtoolsWindow(root)
root.mainloop()