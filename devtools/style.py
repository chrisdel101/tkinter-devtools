
class Style:
    treeview = {
        'background':"black",
        'fieldbackground':"orange",   
    }
    config_listbox_manager = {
        'listbox': {
            'bg': 'grey',
            'width': 50,
            'font': ("Courier New", 14),
        },
        'entry':{
            'borderwidth': 0,
            'highlightthickness': 1,    
            'font': ("Helvetica", 14)
        },
        'key_entry':{
            'takefocus': False
        }
    }
    right_window = {
        'frame': {
            'width': 100,
            'height': 200,
            'bg': 'green',
        },
        'header':{
            'frame':{
                'bg': 'grey',
            },
            'top_row':{
                'frame': {
                    'bg': 'grey'
                },
                'btn1_text': 'Attributes',
                'btn2_text': 'Geometry'
            },
            'bottom_row':{
                'bg': 'grey'
            },
        }
    }
    left_window = {
        'frame': {
        'width': 100,
        'height': 300,
        'bg': 'black',
        }
    }