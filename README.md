**Beta Release**

# Tkinter-devtools

## Browser-like devtools but for Tkinter

Tired of restarting your tkinter app just to see the effect of every little change?

Inspired by browser devtools, Tkinter-devtools is a runtime inspector/editor for Tkinter apps that opens a developer window next to your running app so you can make live changes.

100% Python standard library. ZERO dependencies.


- Inspect the live widget tree structure 
- Switch between widget option editing and geometry editing
- Add/update/remove widget configuration settings
- Highlight the currently selected widgets as you navigate

## Install

    pip install tkinter-devtools

## Quick Start

Just pass your app or root window to the DevtoolsWindow constructor.

```python
import tkinter as tk
from tkinter_devtools import DevtoolsWindow

# random set of test widgets
class TestApp(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        grid_container = tk.Frame(self, padx=10, width=200, height=300)
        tk.Label(self, text="Test App").grid(column=0, row=0)
        tk.Button(self, text="Button").grid(column=0, row=2)
        # Create a canvas widget
        canvas = tk.Canvas(grid_container, width=400, height=300, bg='white')
        canvas.pack()
        # Draw a red rectangle
        canvas.create_rectangle(50, 50, 200, 150, fill="red")
        # Draw a blue oval
        canvas.create_oval(250, 50, 350, 150, fill="blue")
        canvas.create_window(50, 50)
        grid_container.grid()

root = tk.Tk()
app = TestApp(root)
app.pack(side=tk.TOP, fill="both", expand=True)

DevtoolsWindow(app)

root.mainloop()
```

## Options

`DevtoolsWindow(master, **options)` takes these optional keyword arguments.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `devtools_title` | `str` | `'Tkinter-devtools'` | Title of the devtools window. |
| `show_unmapped_widgets` | `bool` | `True` | Show widgets in the tree that are not on screen, i.e. not packed. |
| `skip_runtime_checks` | `bool` | `None` | Skip the Tcl/Tk bridge checks on startup. See [Runtime Safety Checks](#runtime-safety-checks). |
| `logging_level` | `int` | `logging.ERROR` | Log level for devtools messages, e.g. `logging.DEBUG`. |
| `width` | `int` | `700` | Width of the devtools window in pixels. |
| `height` | `int` | `500` | Height of the devtools window in pixels. |
| `x_coord` | `int` | `700` | Distance of the window from the left of the screen in pixels. |
| `y_coord` | `int` | `0` | Distance of the window from the top of the screen in pixels. |

## Runtime Safety Checks

Tkinter-devtools requires a stable Tcl/Tk bridge. On some systems this means `tk.TclVersion <= 8.6`. Modern Python upgraded to `9.0` and this will not work on some systems.

On startup, tests verify that the bridge is working. If it is not, the window will close and the devtools cannot run. You will need to patch your tcl version to `8.6` or another working version.

You can disable these checks with `skip_runtime_checks=True`.

To check your TclVersion:

```bash
python - <<'EOF'        
import tkinter as tk
print("TclVersion:", tk.TclVersion)
print("TkVersion:", tk.TkVersion)
print("Tcl library:", tk._tkinter.__file__)
EOF
```

## Build from source

```bash
git clone https://github.com/chrisdel101/tkinter-devtools.git
```

### Installing package builder

Windows

    py -m pip install --upgrade pip
    py -m pip install --upgrade build
    py -m build

Mac

    python3 -m pip install --upgrade pip && 
    python3 -m pip install --upgrade build &&
    python3 -m build

### Building the wheel

Packaging in source - run this in the tkinter-devtools directory. Removes any previous builds.

    rm -rf build && rm -rf dist && rm -rf src/tkinter_devtools.egg-info && python -m build

Importing in local target - run this in the target application directory. Uninstalls previous first.

    pip uninstall /path/to/package/tkinter_devtools/dist/tkinter_devtools-<current-version>-py3-none-any.whl && pip install /path/to/package/tkinter_devtools/dist/tkinter_devtools-<current-version>-py3-none-any.whl
