from ConfigListbox import ConfigListbox
from windows.WindowFrame import WindowFrame


class RightWindowFrame(WindowFrame):
    def __init__(self, master=None, callback=None):
        super().__init__(master)
        # list of selected widget config values
        self.styles_window_listbox = ConfigListbox(self, width=50, callback=callback)
         # pack listbox
        self.styles_window_listbox.pack(side="left", fill="both", expand=True)

    
