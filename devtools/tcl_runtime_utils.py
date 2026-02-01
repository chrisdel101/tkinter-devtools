from logging import root
import tkinter as tk
from tkinter import ttk

class TclRunTimeUtility:
    @staticmethod
    # check button widget command works
    def assert_button_command_valid(root):
        fired = False

        def _probe():
            nonlocal fired
            fired = True

        btn = tk.Button(root, command=_probe)

        # Critical: invoke does NOT require packing or display
        btn.invoke()

        if not fired:
            raise RuntimeError(
                "Tk command callbacks are not working in this process.\n"
                "This Python/Tk environment is broken."
            )
        btn.destroy()
    @staticmethod
    def assert_combobox_command_valid(root):
        fired = False

        def _probe():
            nonlocal fired
            fired = True

        cbox = ttk.Combobox(root, values=["A", "B", "C"])
        cbox.place()

       
        popdown = root.tk.call("ttk::combobox::PopdownWindow", cbox)

        # Bind <Unmap> to the popdown window
        root.tk.call("bind", popdown, "<Unmap>", root.register(_probe))
        cbox.current(1)
        cbox.set("A") 
        cbox.event_generate("<<ComboboxSelected>>")
        root.after(1000, lambda: cbox.event_generate('<Escape>'))  # Close after 1s
        root.update_idletasks()
        if not fired:
            raise RuntimeError(
                "Tk command callbacks are not working in this process.\n"
                "This Python/Tk environment is broken."
            )
    @staticmethod
    def assert_tk_bridge(root):
        fired = False

        def _probe():
            nonlocal fired
            fired = True

        # 1. Register the Python function as a Tcl command
        cmd_name = root.register(_probe)

        # 2. Use Tcl to call that registered command
        # This proves the Tcl interpreter can talk back to Python
        root.tk.eval(f"{cmd_name}")
        if not fired:
            raise RuntimeError(
                "Tk command callbacks are not working in this process.\n"
                "This Python/Tk environment is broken."
            )
    def runtime_checks(root):
        TclRunTimeUtility.assert_tk_bridge(root)
        TclRunTimeUtility.assert_button_command_valid(root)
