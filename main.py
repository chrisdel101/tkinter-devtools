from tkinter import *
import tkinter as tk
from tkinter import ttk
from devtools.style import Style

from devtools.DevtoolsWindow import DevtoolsWindow
    
class App(tk.Frame):
    def __init__(self, root):
        super().__init__()
        self.pack()


        grid_container = tk.Frame(self, padx=10, width=300, height=200)
        tk.Button(grid_container, text="Quit").grid(column=1, row=1)
        tk.Label(grid_container, text="Hello World!").grid(column=0, row=0)
        tk.Label(grid_container, text="Hello World2!").grid(column=1, row=0)
        grid_container.grid()

        # NEW: a grid-managed holder frame
        # pack_holder = tk.Frame(root_inner_frame, bg="red")
        # pack_holder.grid(column=0, row=2, columnspan=2, sticky="s")

        # force geometry live changes   
        # pack happens ONLY inside this holder
        # tk.Frame(pack_container, width=20, height=20, bg="blue").place()
        grid_container.grid_propagate(False)
        tk.Label(root, text="XXXXXXXXX")#.pack()
    
root = tk.Tk()
app = App(root)
# style = ttk.Style()
# style.configure(
#     "My.Treeview",
#     **Style.treeview
# )
# root.after(100, lambda: DevtoolsWindow(root, title="Devtools"))
DevtoolsWindow(root, title="Devtools", show_unmapped_widgets=True)
root.mainloop()