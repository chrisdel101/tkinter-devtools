import tkinter as tk
from tkinter import ttk

from utils import Utils

class TreeView(ttk.Treeview):
    
    def __init__(self, master, listbox_widget): 
        super().__init__(master, show="tree")
        self.selected_item = None
        self._listbox_widget = listbox_widget
        self.stored_tree_widgets_by_id = {}

    def set_tree_widget_by_id(self, item_id, widget):
        """Store the widget in the dictionary with its ID."""
        self.stored_tree_widgets_by_id[item_id] = widget

    def get_tree_widget_by_id(self, item_id):
        return self.stored_tree_widgets_by_id.get(item_id)
    
    def build_tree(self, parent_widget, parent_node_id=""):
    # check if it's a parent node - parent tree node has ID
        if not parent_node_id:
            parent_widget_id = self.insert("", "end", text=parent_widget.winfo_class())
            self.set_tree_widget_by_id(parent_widget_id, parent_widget)
        else:
            parent_widget_id = parent_node_id
        for child in parent_widget.winfo_children():
            # Exclude any Toplevel windows (like the dev tool)
            if isinstance(child, tk.Toplevel):
                continue
            # ID of place in tree
            child_widget_id = self.insert(parent_widget_id, "end", text=child.winfo_class())
            self.stored_tree_widgets_by_id[child_widget_id] = child  
            self.set_tree_widget_by_id(child_widget_id, child)
            self.build_tree(child, child_widget_id)
    
    # main listener for tree item selects
    def bind_tree_select(self, callback):
        # call func when tree item is selected
        self.bind("<<TreeviewSelect>>", lambda e:
        self.handle_tree_select(e, callback))

    def handle_tree_select(self, _, callback):
            # get selected tree item 
            selected = self.selection()
            if selected and selected != self.selected_item:
                # .selection give tree item ID
                item_id = selected[0]
                # get widget info from store
                self.selected_item = self.get_tree_widget_by_id(item_id)
                # TODO check if current select is already selected
                if self.selected_item:
                    try:
                        # delete prev content in listbox
                        self._listbox_widget.delete_contents()
                        # get config of selected
                        config = self.selected_item.configure()
                        # filter out unwanted config values
                        filtered_config = Utils.filter_config_values(config)
                        # display selected tree item's config in listbox win
                        self._listbox_widget.insert_all(filtered_config)
                        callback(selected_item=self.selected_item)

                    except Exception as e:
                        self._listbox_widget.delete_contents()
                        self._listbox_widget.insert_item(tk.END, f"Error: {e}")

    # select a tree item programatically
    def select_tree_item(self, item):
        self.selection_set(item) 

    def update_tree_item(self, changes_dict):
            self.selected_item.config(**{changes_dict['key']: changes_dict['value']})