from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys

widget_store = {}


def build_widget_tree(parent_widget, tree, parent_node=""):
    node_id = tree.insert(parent_node, "end", text=parent_widget.winfo_class())
    widget_store[node_id] = parent_widget
    for child in parent_widget.winfo_children():
        if getattr(child, "is_devtools", False):
            continue  # Skip devtools window itself
        # Exclude any Toplevel windows (like the dev tool)
        if isinstance(child, tk.Toplevel):
            continue
        
        node_id = tree.insert(parent_node, "end", text=child.winfo_class())
        widget_store[node_id] = child  # Store widget reference
        build_widget_tree(child, tree, node_id)
        # else:
        #     #INNER COLUMNS text= name left column, values= right col
        #     node_id = tree.insert(parent_node, "end", text=child.winfo_class(), values=(str(child)))
        #     build_widget_tree(child, tree, node_id)

def show_widget_properties(widget, text_widget):
    text_widget.delete("1.0", tk.END)
    config = widget.configure()
    for key in config:
        text_widget.insert(tk.END, f"{key}: {config[key][-1]}\n")



def run_code(input_widget, output_widget, context):
    code = input_widget.get("1.0", tk.END)
    try:
        exec(code, context)
    except Exception as e:
        output_widget.insert(tk.END, f"Error: {e}\n")

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)
    def flush(self):
        pass

def on_select(event, tree, props):
    selected = tree.selection()
    if selected:
        item_id = selected[0]
        widget = widget_store.get(item_id)
        if widget:
            try:
                props.delete("1.0", tk.END)
                config = widget.configure()
                for key in config:
                    props.insert(tk.END, f"{key}: {config[key][-1]}\n")
                show_widget_properties(widget, props)
            except Exception as e:
                props.delete("1.0", tk.END)
                props.insert(tk.END, f"Error: {e}")

def open_dev_tools(main_root):
    dev_window = tk.Toplevel(main_root)
    dev_window.title("DevTools")

    tree = ttk.Treeview(dev_window)
    tree.pack(side="left", fill="y")

    props = tk.Text(dev_window, width=50, name="text")
    props.pack(side="left", fill="both", expand=True)

    tree.bind("<<TreeviewSelect>>", lambda e: on_select(e, tree, props))
    build_widget_tree(main_root, tree)



root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Label(frm, text="Hello World2!").grid(column=0, row=1)
ttk.Button(frm, text="Quit").grid(column=1, row=0)
open_dev_tools(root)
root.mainloop()