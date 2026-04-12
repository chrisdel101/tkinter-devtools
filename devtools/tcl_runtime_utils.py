from logging import root
import logging
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
    def runtime_checks(root, include_ttk_popdown_check=False):
        TclRunTimeUtility.assert_tk_bridge(root)
        TclRunTimeUtility.assert_button_command_valid(root)
        # Optional: this probes ttk combobox popdown internals.
        # Keep it opt-in because it validates a specific Tcl/Ttk path,
        # not the core Python<->Tcl callback bridge.
        if include_ttk_popdown_check:
            TclRunTimeUtility.assert_combobox_command_valid(root)
        TclRunTimeUtility.start_worker_after_runtime_probe(root, skip_thread_checks=False)

    @staticmethod
    def start_worker_after_runtime_probe(root, timeout_ms=1200, skip_thread_checks=False):
        """Probe whether worker thread -> root.after(0, cb) is delivered.

        This is intentionally non-blocking and relies on the real app mainloop,
        so it can be used at startup without running a nested event loop.
        """
        if getattr(root, "_devtools_worker_after_probe_started", False):
            return
        setattr(root, "_devtools_worker_after_probe_started", True)

        state = {
            "delivered": False,
            "worker_error": None,
        }

        def _delivered_on_main_thread():
            state["delivered"] = True

        def _worker_probe():
            try:
                # This call is exactly what we want to validate for runtime behavior.
                root.after(0, _delivered_on_main_thread)
            except Exception as exc:
                state["worker_error"] = exc

        def _fail(message):
            if skip_thread_checks:
                logging.warning(
                    f"{message} Continuing because skip_thread_checks=True."
                )
                return
            logging.error(message)
            raise SystemExit(message)

        def _poll_remaining(remaining_ms):
            if state["delivered"]:
                return
            if state["worker_error"] is not None:
                _fail(
                    "Worker thread could not call Tk after(0, callback). "
                    "Cross-thread Tk callback delivery is broken in this runtime."
                )
                return
            if remaining_ms <= 0:
                _fail(
                    "Threading probe failed for runtime version of tcl/tk. Threads will not work properly with this version. Set skip_thread_checks=True to run anyway. "
                )
                return
            root.after(25, lambda: _poll_remaining(remaining_ms - 25))

        threading.Thread(target=_worker_probe, daemon=True).start()
        root.after(0, lambda: _poll_remaining(timeout_ms))
