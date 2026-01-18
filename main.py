from tkinter import *
import tkinter as tk
from tkinter import ttk
from devtools.style import Style

from devtools.DevtoolsWindow import DevtoolsWindow
    
root = Tk()
# style = ttk.Style()
# style.configure(
#     "My.Treeview",
#     **Style.treeview
# )
pack_container = tk.Frame(root)
pack_container.pack()


grid_container = tk.Frame(pack_container, padx=10, width=300, height=200)
tk.Label(grid_container, text="Hello World!").grid(column=0, row=0)
tk.Label(grid_container, text="Hello World2!").grid(column=1, row=0)
tk.Button(grid_container, text="Quit").grid(column=3, row=1)

# NEW: a grid-managed holder frame
# pack_holder = tk.Frame(root_inner_frame, bg="red")
# pack_holder.grid(column=0, row=2, columnspan=2, sticky="s")

grid_container.grid()
# force geometry live changes   
# pack happens ONLY inside this holder
# tk.Frame(pack_container, width=20, height=20, bg="blue").place()
grid_container.grid_propagate(False)
DevtoolsWindow(pack_container, title="Devtools Example")
root.mainloop()