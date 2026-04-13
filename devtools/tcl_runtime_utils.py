import logging
import threading
import tkinter as tk
from tkinter import ttk

class TclRunTimeUtility:
    @staticmethod
    # Verify that a basic Tk button command can round-trip into Python.
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
    # Verify that ttk combobox popdown events still trigger Python callbacks.
    def assert_combobox_command_valid(root):
        fired = False
        command_name = None

        def _probe():
            nonlocal fired
            fired = True

        cbox = ttk.Combobox(root, values=["A", "B", "C"])
        cbox.place()
        root.update_idletasks()

        # Get the popdown window path (does NOT open it)
        popdown = root.tk.call("ttk::combobox::PopdownWindow", cbox)

        # Bind <Unmap> to the popdown window
        command_name = root.register(_probe)
        root.tk.call("bind", popdown, "<Unmap>", command_name)

        # Actually open (map) the popdown via the internal Tcl post command
        root.tk.call("ttk::combobox::Post", cbox)
        root.update()

        # Close it - this triggers <Unmap> on the popdown
        # Use Tcl Unpost directly - Escape via event_generate won't fire without focus
        root.tk.call("ttk::combobox::Unpost", cbox)
        root.update()

        cbox.destroy()
        if command_name:
            # Remove registered Tcl command so teardown does not reference stale callbacks.
            root.deletecommand(command_name)
        if not fired:
            raise RuntimeError(
                "Tk command callbacks are not working in this process.\n"
                "This Python/Tk environment is broken."
            )
    @staticmethod
    # Verify the raw Tcl interpreter can invoke a registered Python callback.
    def assert_tk_bridge(root):
        fired = False
        cmd_name = None

        def _probe():
            nonlocal fired
            fired = True

        # 1. Register the Python function as a Tcl command
        cmd_name = root.register(_probe)

        # 2. Use Tcl to call that registered command
        # This proves the Tcl interpreter can talk back to Python
        root.tk.eval(f"{cmd_name}")
        if cmd_name:
            root.deletecommand(cmd_name)
        if not fired:
            raise RuntimeError(
                "Tk command callbacks are not working in this process.\n"
                "This Python/Tk environment is broken."
            )

    @staticmethod
    # Run startup checks for the core Tk bridge and optional ttk-specific behavior.
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
    # Probe cross-thread delivery by having a worker schedule a main-thread callback.
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
            "done": False,
            "after_ids": set(),
        }

        def _delivered_on_main_thread():
            if state["done"]:
                return
            state["delivered"] = True
            state["done"] = True

        # Cancel any queued polling callbacks before teardown or hard failure.
        def _cancel_pending_after():
            for after_id in tuple(state["after_ids"]):
                try:
                    root.after_cancel(after_id)
                except tk.TclError:
                    pass
            state["after_ids"].clear()

        # Run from a worker thread to validate thread-to-Tk callback scheduling.
        def _worker_probe():
            try:
                # This call is exactly what we want to validate for runtime behavior.
                root.after(0, _delivered_on_main_thread)
            except Exception as exc:
                state["worker_error"] = exc

        # Either downgrade the failure to a warning or stop startup immediately.
        def _fail(message):
            state["done"] = True
            _cancel_pending_after()
            if skip_thread_checks:
                logging.warning(
                    f"{message} Continuing because skip_thread_checks=True."
                )
                return
            raise SystemExit(message)

        # Schedule callbacks defensively so probe shutdown does not leave stale Tcl jobs.
        def _schedule_after(delay_ms, callback, *args):
            """Schedule callbacks only while root exists and probe is active."""
            if state["done"]:
                return None
            after_ref = {"id": None}

            def _wrapped_callback():
                after_id = after_ref.get("id")
                if after_id:
                    state["after_ids"].discard(after_id)
                if state["done"]:
                    return
                callback(*args)

            try:
                if not root.winfo_exists():
                    state["done"] = True
                    return None
                after_id = root.after(delay_ms, _wrapped_callback)
                after_ref["id"] = after_id
                state["after_ids"].add(after_id)
                return after_id
            except tk.TclError:
                state["done"] = True
                return None

        # Stop the probe cleanly if the root is being destroyed.
        def _on_root_destroy(event):
            if event.widget is root:
                state["done"] = True
                _cancel_pending_after()

        # Poll until the worker-scheduled callback lands or the timeout expires.
        def _poll_remaining(remaining_ms):
            if state["done"]:
                return
            if state["delivered"]:
                state["done"] = True
                _cancel_pending_after()
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
            _schedule_after(25, _poll_remaining, remaining_ms - 25)

        root.bind("<Destroy>", _on_root_destroy, add="+")
        threading.Thread(target=_worker_probe, daemon=True).start()
        _schedule_after(0, _poll_remaining, timeout_ms)
