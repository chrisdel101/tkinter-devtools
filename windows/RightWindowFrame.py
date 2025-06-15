from ConfigListbox import ConfigListbox
from windows.WindowFrame import WindowFrame
import tkinter as tk

class RightWindowFrame(WindowFrame):
    def __init__(self, master=None, callback=None):
        super().__init__(master)
        self.header_frame = tk.Frame(self, height=30, bg="lightgrey")
        self.callback = callback
        # list of selected widget config values
        self.styles_window_listbox = ConfigListbox(self, width=50, callback=callback)
        self.add_config_button = tk.Button(self.header_frame, text="+", command=self.handle_add)
        self.subtract_config_button = tk.Button(self.header_frame, text="-", command=self.handle_subract)
        self.add_config_button.pack(side="left", padx=5, pady=5)
        self.subtract_config_button.pack(side="left", padx=5, pady=5)
         # pack listbox
        self.header_frame.pack(side="top", fill="x", expand=False, padx=0, pady=0, ipady=0, ipadx=0)
        self.styles_window_listbox.pack(side="left", fill="both", expand=True)

    
    def handle_add(self):
        current_selection = self.styles_window_listbox.curselection()
        # if none selected insert at top
        if len(current_selection) == 0:
            self.styles_window_listbox.insert(0, "")
            self.styles_window_listbox.handle_entry(0, self.callback)
        # insert after selected_item
        else:
            #  get selected tuple 
            current_selection_index = current_selection[0]
            self.styles_window_listbox.insert(current_selection_index+1, "")
            self.styles_window_listbox.handle_entry(current_selection_index+1, self.callback)

    def handle_subract(self):
        current_selection = self.styles_window_listbox.curselection()
        
        if len(current_selection) == 0:
            print("No item selected to remove.")
            return
        else:
            current_selection_index = current_selection[0]
            self.styles_window_listbox.delete(current_selection_index)