from tkinter import *
import tkinter as tk
from tkinter import ttk
from devtools.style import Style

from devtools.DevtoolsWindow import DevtoolsWindow
    
class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.pack()


        grid_container = tk.Frame(self, padx=10, width=200, height=200)
        tk.Button(self, text="Quit").grid(column=1, row=1)
        tk.Label(self, text="Hello World!").grid(column=0, row=0)
        tk.Label(self, text="Hello World2!").grid(column=1, row=0)
        # Create a canvas widget
        canvas = tk.Canvas(grid_container, width=400, height=300, bg='white')
        canvas.pack()

        # Draw a red rectangle
        canvas.create_rectangle(50, 50, 200, 150, fill="red")

        # Draw a blue oval
        canvas.create_oval(250, 50, 350, 150, fill="blue")

        # Add some text
        canvas.create_text(200, 250, text="This is a canvas", font=("Helvetica", 16))
        btn = tk.Button(canvas, text="I am in a Canvas")
        canvas.create_window(50, 50, window=btn)
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
DevtoolsWindow(root, title="Devtools", show_unmapped_widgets=True)
# root.after(100, lambda: DevtoolsWindow(root, title="Devtools"))
root.mainloop()