from logging import root
import threading
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
        root.update_idletasks()

        # Get the popdown window path (does NOT open it)
        popdown = root.tk.call("ttk::combobox::PopdownWindow", cbox)

        # Bind <Unmap> to the popdown window
        root.tk.call("bind", popdown, "<Unmap>", root.register(_probe))

        # Actually open (map) the popdown via the internal Tcl post command
        root.tk.call("ttk::combobox::Post", cbox)
        root.update()

        # Close it - this triggers <Unmap> on the popdown
        # Use Tcl Unpost directly - Escape via event_generate won't fire without focus
        root.tk.call("ttk::combobox::Unpost", cbox)
        root.update()

        cbox.destroy()
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
    @staticmethod
    def assert_worker_thread_after_delivery(root):
        """Checks whether after(0, callback) from a worker thread is actually
        delivered when the mainloop is running.

        On Tk 8.6 (properly configured): delivery works → PASS.
        On Tk 9.0: after(0, cb) is silently discarded → FAIL.

        A mini mainloop is used because after() from a worker thread requires
        the event loop to be running to dispatch callbacks.

        Fix: use a queue + after(ms, drain) polling loop on the main thread.
        """
        delivered = []
        timeout_id = [None]

        def on_delivery():
            delivered.append(True)
            if timeout_id[0]:
                root.after_cancel(timeout_id[0])
            root.quit()

        def worker():
            try:
                root.after(0, on_delivery)
            except Exception:
                root.after(0, root.quit)

        root.after(50, lambda: threading.Thread(target=worker, daemon=True).start())
        timeout_id[0] = root.after(500, root.quit)  # safety timeout
        root.mainloop()

        if not delivered:
            raise RuntimeError(
                "Worker thread after(0, callback) is not delivered to the main thread.\n"
                "Use a queue + after(ms, drain) pattern for cross-thread GUI updates."
            )

    def runtime_checks(root, include_ttk_popdown_check=True, include_thread_check=True):
        TclRunTimeUtility.assert_tk_bridge(root)
        TclRunTimeUtility.assert_button_command_valid(root)
        # Optional: probes ttk combobox popdown internals via Tcl-level event binding.
        if include_ttk_popdown_check:
            TclRunTimeUtility.assert_combobox_command_valid(root)
        # Optional: confirms after(0, cb) from a worker thread reaches the main thread.
        # Fails on both Tk 8.6 and 9.0 without the queue+drain fix in the caller.
        if include_thread_check:
            TclRunTimeUtility.assert_worker_thread_after_delivery(root)
