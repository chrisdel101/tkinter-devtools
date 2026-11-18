import logging
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter_devtools import DevtoolsWindow
#

    
class TestApp(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.pack()


        grid_container = tk.Frame(self, padx=10, width=200, height=300)#.grid()
        ttk.Button(self, text="Quit").grid(column=1, row=1)
        ttk.Label(self, text="Hello World!")#.grid(column=0, row=0)
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

       
        grid_container.grid_propagate(False)
        tk.Label(self, text="XXXXXXXXX").place(in_=self)
    
root = tk.Tk()
app = TestApp(root)


app.pack(fill="both", expand=True)

DevtoolsWindow(app,
skip_runtime_checks=False, logging_level=logging.DEBUG)
root.mainloop()