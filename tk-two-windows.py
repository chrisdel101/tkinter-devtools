from tkinter import *
from tkinter import ttk
import tkinter as tk

from DevtoolsWindow import DevtoolsWindow

def open_dev_tools(main_root):
    # # main devtools window
    dev_window = DevtoolsWindow(main_root)
    
root = Tk()
root_inner_frame = tk.Frame(root, padx=10, width=300, height=200)
tk.Label(root_inner_frame, text="Hello World!").grid(column=0, row=0)
tk.Label(root_inner_frame, text="Hello World2!").grid(column=0, row=1)
tk.Button(root_inner_frame, text="Quit").grid(column=1, row=0)
root_inner_frame.grid()
# force geometry live changes 
root_inner_frame.grid_propagate(False)
DevtoolsWindow(root)
root.mainloop()