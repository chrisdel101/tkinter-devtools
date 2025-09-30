import tkinter as tk
from windows.LeftWindowFrame import LeftWindowFrame
from windows.RightWindowFrame import RightWindowFrame

class DevtoolsWindow:
    def __init__(self, root, title="Devtools"):
        # Toplevel is the window itself that opens
        self.top_level = tk.Toplevel(root, background='red')
        self.top_level.title(title)
        self.root = root
                
        # right window
        self.right_window = RightWindowFrame(master=self.top_level, set_tree_item_callback=self.set_tree_item_from_entry_value,
        get_tree_item_callback=self.get_current_node_selected)
        # left window
        self.left_window = LeftWindowFrame(root=root, master=self.top_level, listbox_widget=self.right_window.styles_window_listbox, callback=self.set_current_node_selected)

        # pack left window
        self.left_window.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack left window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)

        
    def set_tree_item_from_entry_value(self, _, changes_dict):
        self.left_window.tree.update_tree_item(changes_dict)
    # on treeview select call and store the node
    def set_current_node_selected(self, selected_item):
        self.selected_item = selected_item

    def get_current_node_selected(self):
        return self.selected_item

