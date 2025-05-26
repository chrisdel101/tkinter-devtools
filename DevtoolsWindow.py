import tkinter as tk
from tkinter import Widget, ttk

from ConfigListbox import ConfigListbox

class DevtoolsWindow:
    def __init__(self, root, title="Devtools"):
        # Toplevel is wrapper for two inner windows - does not pack
        self.top_level = tk.Toplevel(root)
        self.top_level.title(title)

        # right window - tree struct inside tool
        self.tree = ttk.Treeview(self.top_level)
        self.tree.pack(side="left", fill="y")
        # left window - list of tree config
        self.tree_item = None
        self.styles_window_listbox = ConfigListbox(self.top_level, width=50, callback=self.get_editted_value)
        self.styles_window_listbox.pack(side="left", fill="both", expand=True)
        self.store_tree_by_id = {}
        
    def build_tree(self, parent_widget, parent_node_id=""):
        # check if it's a parent node - parent tree node has ID
        if not parent_node_id:
            parent_widget_id = self.tree.insert("", "end", text=parent_widget.winfo_class())
            self.store_tree_by_id[parent_widget_id] = parent_widget
        else:
            parent_widget_id = parent_node_id
        for child in parent_widget.winfo_children():
            # Exclude any Toplevel windows (like the dev tool)
            if isinstance(child, tk.Toplevel):
                continue
            # ID of place in tree
            child_widget_id = self.tree.insert(parent_widget_id, "end", text=child.winfo_class())
            self.store_tree_by_id[child_widget_id] = child  
            self.build_tree(child, child_widget_id)

    def handle_tree_select(self, _):
            # get selected tree item 
            selected = self.tree.selection()
            if selected and selected != self.tree_item:
                # .selection give tree item ID
                item_id = selected[0]
                # get widget info from store
                self.tree_item = self.store_tree_by_id.get(item_id)
                # TODO check if current select is already selected
                
                if self.tree_item:
                    try:
                        # delete prev content in listbox
                        self.styles_window_listbox.delete_contents()
                        config = self.tree_item.configure()
                        # display selected tree item's config in listbox win
                        self.styles_window_listbox.insert_all(config) 
        
                                    
                        # add listener to listbox - when clicked callback will fire
                        # self.styles_window_listbox.bind("<Double-1>", self.styles_window_listbox._start_edit)
                        # delete_contentshandle_item_click(e, self.update_tree_item, tree_item)                      
                    except Exception as e:  
                        self.styles_window_listbox.delete_contents()
                        self.styles_window_listbox.insert_item(tk.END, f"Error: {e}")
    # main listener for tree item selects
    def attach_tree_select(self):
        self.tree.bind("<<TreeviewSelect>>", lambda e:
        self.handle_tree_select(e))
    # select a tree item programatically
    def select_tree_item(self, item):
        self.tree.selection_set(item)  

    def update_tree_item(self,tree_item):
        tree_item.config(text="New Text")

    def update_listbox_item(self, widget, index, key, value):
        # remove old item
        widget.delete(index)
        # add new item
        widget.insert(index, f"{key}: {value}")
    
    
    def handle_item_click(self, e, callback, tree_item):
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
                self.update_listbox_item(widget, index, key, value)
                # update tree item
                callback(tree_item)

        else:
                # no item selected
            print("Error in selecting")
            
    def get_editted_value(self, e):
        print(self.tree_item)
        print("TESTSTIN", str(e), str(self.tree_item))   
