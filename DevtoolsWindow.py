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
        self.right_window = RightWindowFrame(master=self.top_level, callback=self.get_editted_value)
        # left window
        self.left_window = LeftWindowFrame(root=root, master=self.top_level, listbox_widget=self.right_window.styles_window_listbox)

        # pack left window
        self.left_window.tree.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)
        # pack left window
        self.right_window.pack(side="left", fill="both", expand=True, padx=0, pady=0, ipady=0, ipadx=0)

        
    def get_editted_value(self, e, changes_dict):
        self.tree.update_tree_item(changes_dict)   
    
    

