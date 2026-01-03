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

# NEW: a grid-managed holder frame
pack_holder = tk.Frame(root_inner_frame, bg="red")
pack_holder.grid(column=0, row=2, columnspan=2, sticky="s")

# pack happens ONLY inside this holder
tk.Frame(pack_holder, width=100, height=50, bg="blue").place(
    relx=0.5, rely=0.5, anchor=CENTER
)
root_inner_frame.grid()
# force geometry live changes   
root_inner_frame.grid_propagate(False)
DevtoolsWindow(root)
root.mainloop()