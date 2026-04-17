IN DEVELOPMENT - beta release shortly

# Tk-DevTools

# Browser-like devtools but for Tkinter

Tired of restarting your tkinter app just to see the effect of every little change?

Inspired by browser devtools, Tk-DevTools is a runtime inspector/editor for Tkinter apps. 100% python standard library.

It lets you open a developer window next to your running app and make live changes.

- Inspect the live widget tree structure 
- Switch between widget option editing and geometry editing
- Add/update/remove widget configurations settings
- Highlights the currently selected widgets as you navigate

## Install

## Quick Start

Just pass your app or root window to the DevtoolsWindow constructor.

```python
import tkinter as tk
from devtools.DevtoolsWindow import DevtoolsWindow

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

DevtoolsWindow(
    root,
    title="Devtools",
    show_unmapped_widgets=False,
)

root.mainloop()
```

## Runtime Safety Checks

Tk-Devtools requies an stable tk-tlc bridge. On some systems this means `tk.TclVersion <= 8.6`. The devtools will not work without a stable bridge.

On startup a few test run to verify this bridge is working, else the window will close.

You can disable these checks with `skip_runtime_checks=True`.

To check your TclVersion

```python
python - <<'EOF'        
import tkinter as tk
print("TclVersion:", tk.TclVersion)
print("TkVersion:", tk.TkVersion)
print("Tcl library:", tk._tkinter.__file__)
EOF
```

