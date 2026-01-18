
from tkinter import ttk


class Style:
    def __init__(self, root=None):
        tree_style = ttk.Style(root)
        tree_style.configure(
            "My.Treeview",
            **self.treeview
        )
        tree_style.map(
        "Treeview",
        background=[("selected", "grey")],
        foreground=[("selected", "black")]
    )
    left_window = {
        'frame': {
            # 'font': ("Courier New", 14),

            # 'width': 300,
            # 'height': 300,
            # 'bg': 'red',
        }
    }
    treeview = {
        "selectbackground": "yellow",
        'font': ("Helvetica New", 13),
        'fieldbackground': "#C0C0C0",
        'background': "#C0C0C0",  # bg does not work here
        "foreground": "#000",  # fg does not work here
    }
    config_listbox_manager = {
        'listbox': {
            'bg': '#F5F5F5',
            'width': 50,
            'font': ("Courier New", 14),
            'fg': "#000"
        },
        'entry': {
            'borderwidth': 0,
            'highlightthickness': 1,
            'font': ("Helvetica", 14)
        },
        'key_entry': {
            'takefocus': False
        },
        "item-disabled": {
            "fg": "#777777",                
            "selectforeground": "#777777",  
            "selectbackground": "#d9d9d9", 
            "background": "#d9d9d9",
    }
    }
    right_window = {
        'frame': {
            'width': 100,
            'height': 200,
            'bg': 'green',
        },
        'header': {
            'frame': {
                'bg': 'grey',
            },
            'top_row': {
                'frame': {
                    'bg': 'grey'
                },
                'option_button_text': 'Options',
                'geo_button_text': 'Geometry'
            },
            'bottom_row': {
                'bg': 'grey'
            },
        }
    }
    
    

