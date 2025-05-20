import tkinter as tk
from tkinter import ttk

class DevtoolsWindow:
    def __init__(self, root, title="Devtools"):
        # Toplevel is wrapper for two inner windows - does not pack
        self.top_level = tk.Toplevel(root)
        self.top_level.title(title)

        # right window - tree struct inside tool
        self.tree = ttk.Treeview(self.top_level)
        self.tree.pack(side="left", fill="y")
        # left window - list of tree config
        self.styles_window_listbox = tk.Listbox(self.top_level, width=50, name="text")
        self.styles_window_listbox.pack(side="left", fill="both", expand=True)

        self.tree_items_store = {}
        
    def build_tree(self, parent_widget, parent_node_id=""):
        # check if it's a parent node - parent tree node has ID
        if not parent_node_id:
            parent_widget_id = self.tree.insert("", "end", text=parent_widget.winfo_class())
            self.tree_items_store[parent_widget_id] = parent_widget
        else:
            parent_widget_id = parent_node_id
        for child in parent_widget.winfo_children():
            # Exclude any Toplevel windows (like the dev tool)
            if isinstance(child, tk.Toplevel):
                continue
            # ID of place in tree
            child_widget_id = self.tree.insert(parent_widget_id, "end", text=child.winfo_class())
            self.tree_items_store[child_widget_id] = child  
            self.build_tree(child, child_widget_id)

    def attach_tree_select(self):
        self.tree.bind("<<TreeviewSelect>>", lambda e:
        self._handle_tree_select(e, self.tree, self.styles_window_listbox))
    
    def select_tree_item(self, item):
        self.tree.selection_set(item)  
        
    def _handle_tree_select(self, _, tree, styles_window_listbox):
        # get selected tree item 
        selected = self.tree.selection()
        if selected:
            # .selection give tree item ID
            item_id = selected[0]
            # get widget info from store
            tree_item = self.tree_items_store.get(item_id)
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
            
