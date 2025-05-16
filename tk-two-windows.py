from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys

# track widgets by tree insert ID
widget_store = {}


def build_widget_tree(parent_widget, tree, parent_node_id=""):
    # check if it's a parent node - parent tree node has ID
    if not parent_node_id:
        parent_widget_id = tree.insert("", "end", text=parent_widget.winfo_class())
        widget_store[parent_widget_id] = parent_widget
    else:
        parent_widget_id = parent_node_id
    for child in parent_widget.winfo_children():
        if getattr(child, "is_devtools", False):
            continue  # Skip devtools window itself
        # Exclude any Toplevel windows (like the dev tool)
        if isinstance(child, tk.Toplevel):
            continue
        # ID of place in tree
        child_widget_id = tree.insert(parent_widget_id, "end", text=child.winfo_class())
        widget_store[child_widget_id] = child  
        build_widget_tree(child, tree, child_widget_id)
        

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

def insert_selected_styles(styles_window: Widget, config_dict: dict):
    for key in config_dict:
        # insert selected node into styles_window window
        styles_window.insert(tk.END, f"{key}: {config_dict[key][-1]}\n")
    # set bind listener
    styles_window.bind("<ButtonRelease-1>", handle_styles_select)

def handle_styles_select(e):
    print("Clicked on styles window")
    
def handle_tree_select(_, tree, styles_window):
    # get selected tree item 
    selected = tree.selection()
    if selected:
        item_id = selected[0]
        widget = widget_store.get(item_id)
        if widget:
            try:
                styles_window.delete("1.0", tk.END)
                config = widget.configure()
                # display config in left window
                insert_selected_styles(styles_window, config)                
            except Exception as e:
                styles_window.delete("1.0", tk.END)
                styles_window.insert(tk.END, f"Error: {e}")

def manual_select(selected_widget, styles_window):
    
    if not selected_widget:
        return
    
    try:
        styles_window.delete("1.0", tk.END)
        config = selected_widget.configure()
        # display config in left window
        insert_selected_styles(styles_window, config)                
        # show_widget_properties(widget, styles_window)
    except Exception as e:
        styles_window.delete("1.0", tk.END)
        styles_window.insert(tk.END, f"Error: {e}")

def open_dev_tools(main_root):
    # main devtools window
    dev_window = tk.Toplevel(main_root)
    dev_window.title("DevTools")
    # tree struct inside tool
    tree = ttk.Treeview(dev_window)
    tree.pack(side="left", fill="y")
    # added window to left to hold styles
    styles_window = tk.Text(dev_window, width=50, name="text")
    styles_window.pack(side="left", fill="both", expand=True)

    tree.bind("<<TreeviewSelect>>", lambda e: handle_tree_select(e, tree, styles_window))
    build_widget_tree(main_root, tree)
    # select top layer on load
    tree.selection_set(tree.get_children()[0])  # Select the first item by default



root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Label(frm, text="Hello World2!").grid(column=0, row=1)
ttk.Button(frm, text="Quit").grid(column=1, row=0)
open_dev_tools(root)
root.mainloop()