from tkinter import *
from tkinter import ttk
import tkinter as tk
import sys

from Devtools import DevtoolsWindow

# track widgets by tree insert ID
tree_items_store = {}


def build_widget_tree(parent_widget, tree, parent_node_id=""):
    # check if it's a parent node - parent tree node has ID
    if not parent_node_id:
        parent_widget_id = tree.insert("", "end", text=parent_widget.winfo_class())
        tree_items_store[parent_widget_id] = parent_widget
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
        tree_items_store[child_widget_id] = child  
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

def insert_selected_styles(styles_window_listbox: Widget, config_dict: dict):
    for key in config_dict:
        # insert selected node into styles_window_listbox window
        styles_window_listbox.insert(tk.END, f"{key}: {config_dict[key][-1]}\n")

def update_tree_item(tree_item):
    tree_item.config(text="New Text")

def update_listbox_item(widget, index, key, value):
    # remove old item
    widget.delete(index)
    # add new item
    widget.insert(index, f"{key}: {value}")


def handle_listbox_click(e, callback, tree_item):
    clicked_listbox_item: tuple = e.widget.curselection()
    if clicked_listbox_item:
        # get the index of the selected listbox item
        index = clicked_listbox_item[0]
        # get   the widget from the event
        widget = e.widget
        # get the value of the selected item
        list_item_str = widget.get(index)
        split_list_items: list = list_item_str.split(":")
        key = split_list_items[0]
        value = split_list_items[1]
        # print the list_item_str
        if len(split_list_items) >= 2 and split_list_items[1].strip() == "Hello World!":
            # get the value of the selected item
            print("Selected item:", value.strip())
            update_listbox_item(widget, index, key, value)
            # update tree item
            callback(tree_item)

    else:
            # no item selected
        print("Error in selecting")
    
def handle_tree_select(_, tree, styles_window_listbox):
    # get selected tree item 
    selected = tree.selection()
    if selected:
        # .selection give tree item ID
        item_id = selected[0]
        # get widget info from store
        tree_item = tree_items_store.get(item_id)
        if tree_item:
            try:
                # delete prev content in window
                styles_window_listbox.delete(0, tk.END)
                config = tree_item.configure()
                # display selected tree item's config in style window
                insert_selected_styles(styles_window_listbox, config) 
                # add listener to styles listbox
                styles_window_listbox.bind("<ButtonRelease-1>", lambda e: handle_listbox_click(e, update_tree_item, tree_item))                      
            except Exception as e:  
                styles_window_listbox.delete(0, tk.END)
                styles_window_listbox.insert(tk.END, f"Error: {e}")

def manual_select(selected_widget, styles_window_listbox):
    
    if not selected_widget:
        return
    
    try:
        styles_window_listbox.delete("1.0", tk.END)
        config = selected_widget.configure()
        # display config in left window
        insert_selected_styles(styles_window_listbox, config)                
        # show_widget_properties(widget, styles_window_listbox)
    except Exception as e:
        styles_window_listbox.delete("1.0", tk.END)
        styles_window_listbox.insert(tk.END, f"Error: {e}")

def open_dev_tools(main_root):
    # # main devtools window
    # dev_window = tk.Toplevel(main_root)
    # dev_window.title("DevTools")
    # # tree struct inside tool
    # tree = ttk.Treeview(dev_window)
    # tree.pack(side="left", fill="y")
    dev_window = DevtoolsWindow(main_root)
    dev_window.attach_tree_select()
    dev_window.build_tree(root)
    # added window to left to hold styles
    # styles_window_listbox = tk.Listbox(dev_window, width=50, name="text")
    # styles_window_listbox.pack(side="left", fill="both", expand=True)

    # tree.bind("<<TreeviewSelect>>", lambda e: handle_tree_select(e, tree, styles_window_listbox))
    
    # build_widget_tree(main_root, tree)
    # select top layer on load - this runs the TreeviewSelect listener  
    dev_window.select_tree_item(dev_window.tree.get_children()[0])  # Select the first item by default



root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Label(frm, text="Hello World2!").grid(column=0, row=1)
ttk.Button(frm, text="Quit").grid(column=1, row=0)
open_dev_tools(root)
root.mainloop()