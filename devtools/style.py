
from tkinter import ttk


class Style:
    def __init__(self, master=None):
        tree_style = ttk.Style(master)
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
        'background': "#C0C0C0",  # bg version does not work here - must be long version
        "foreground": "#000",  # fg version does not work here
        "highlightbackground": "#FF4500",
        "highlightthickness": 2,
    }
    devtools_window = {
        'geometry': '700x500+700+0',
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
            'height': 300,
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
            'row_shift_buttons': {
                # Single disabled style shared by both +/- controls.
                'disabled': {
                    'disabledforeground': '#d0d0d0',
                    'highlightbackground': '#2f2f2f',
                },
            },
        }
        ,
        'row_shift_tooltip': {
            'text': 'Disabled. All options shown',
            'x_offset': 16,
            'y_offset': 6,
            'label': {
                'bg': '#fff8dc',
                'fg': '#222222',
                'relief': 'solid',
                'bd': 1,
                'padx': 6,
                'pady': 3,
            }
        }
    }
    
    

