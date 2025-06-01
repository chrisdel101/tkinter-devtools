import tkinter as tk
from tkinter import Widget, ttk

from ConfigListbox import ConfigListbox

class DevtoolsWindow:
    def __init__(self, root, title="Devtools"):
        # Toplevel is wrapper for two inner windows - does not pack
        self.top_level = tk.Toplevel(root)
        self.top_level.title(title)
        self.root = root
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
                        # filter out unwanted config values
                        config = self.filter_config_values(config)
                        # display selected tree item's config in listbox win
                        self.styles_window_listbox.insert_all(config) 
                                    
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

    def update_tree_item(self, changes_dict):
        self.tree_item.config(**{changes_dict['key']: changes_dict['value']})
    
    def get_editted_value(self, e, changes_dict):
        self.update_tree_item(changes_dict)   

    def config_value_helper(self, value):
        # Convert to string for simple checks
        val_str = str(value).strip().lower()

        # Skip empty or zero-like values
        if val_str in ('', '0', 'none', 'false'):
            return False

        # Skip values starting with dash (like '-borderwidth', '-background')
        if val_str.startswith('-'):
            return False
        

        # Skip system placeholders or common "default" words (case-insensitive)
        system_defaults = [
            'systemwindowbackgroundcolor',
            'systemtextcolor',
            'systemhighlightcolor',
            'systemhighlightbackground',
            'systembuttonface',
            'systembuttontext',
            'systemwindowtext',
            'systembuttonshadow',
            'systempressedbuttontextcolor',
            'tkdefaultfont'
        ]
        if val_str in system_defaults:
            return False

        return True

    def config_key_helper(self, key):
        # filter out class - cannot be changed
        if key != "class":
            return True
        return False
    
    def filter_config_values(self, config):
        filtered = {}
        for key, values in config.items():
            # The "actual value" may be the last element? Or you pick which?
            # From your example, the last element seems to be the current value
            current_value = values[-1]
            if not self.config_key_helper(key):
                continue
            if self.config_value_helper(current_value):
                filtered[key] = current_value
        return filtered

