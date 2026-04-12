import threading
import queue
import unittest
import tkinter as tk
from tkinter import ttk
from unittest.mock import patch

from devtools.tcl_runtime_utils import TclRunTimeUtility


class TclRuntimeUtilsTests(unittest.TestCase):
   def setUp(self):
      self.root = tk.Tk()
      self.root.withdraw()

   def tearDown(self):
      self.root.destroy()

   # ------------------------------------------------------------------ #
   # assert_tk_bridge                                                     #
   # ------------------------------------------------------------------ #

   def test_assert_tk_bridge_passes_with_working_bridge(self):
      TclRunTimeUtility.assert_tk_bridge(self.root)

   def test_assert_tk_bridge_raises_when_bridge_broken(self):
      real_register = self.root.register
      self.root.tk.eval("proc __noop__ {args} {}")

      def _broken_register(func, *args, **kwargs):
         return "__noop__"

      self.root.register = _broken_register
      try:
         with self.assertRaises(RuntimeError):
            TclRunTimeUtility.assert_tk_bridge(self.root)
      finally:
         self.root.register = real_register

   # ------------------------------------------------------------------ #
   # assert_button_command_valid                                          #
   # ------------------------------------------------------------------ #

   def test_assert_button_command_passes_with_working_bridge(self):
      TclRunTimeUtility.assert_button_command_valid(self.root)

   def test_assert_button_command_raises_when_bridge_broken(self):
      # Misc._register = register is a class-level alias bound at definition time,
      # so patching Misc.register alone is insufficient - _options() calls self._register().
      # Both must be patched to intercept Button's command registration.
      self.root.tk.eval("proc __noop__ {args} {}")
      with patch("tkinter.Misc.register", return_value="__noop__"), \
           patch("tkinter.Misc._register", return_value="__noop__"):
         with self.assertRaises(RuntimeError):
            TclRunTimeUtility.assert_button_command_valid(self.root)

   # ------------------------------------------------------------------ #
   # assert_combobox_command_valid                                        #
   # ------------------------------------------------------------------ #

   def test_assert_combobox_passes_with_working_bridge(self):
      TclRunTimeUtility.assert_combobox_command_valid(self.root)

   def test_assert_combobox_raises_when_bridge_broken(self):
      real_register = self.root.register
      self.root.tk.eval("proc __noop__ {args} {}")

      def _broken_register(func, *args, **kwargs):
         return "__noop__"

      self.root.register = _broken_register
      try:
         with self.assertRaises(RuntimeError):
            TclRunTimeUtility.assert_combobox_command_valid(self.root)
      finally:
         self.root.register = real_register

   # ------------------------------------------------------------------ #
   # runtime_checks                                                       #
   # ------------------------------------------------------------------ #

   def test_runtime_checks_passes_default(self):
      TclRunTimeUtility.runtime_checks(self.root)

   def test_runtime_checks_passes_with_ttk_popdown(self):
      TclRunTimeUtility.runtime_checks(self.root, include_ttk_popdown_check=True)

   def test_runtime_checks_raises_when_bridge_broken(self):
      real_register = self.root.register
      self.root.tk.eval("proc __noop__ {args} {}")

      def _broken_register(func, *args, **kwargs):
         return "__noop__"

      self.root.register = _broken_register
      try:
         with self.assertRaises(RuntimeError):
            TclRunTimeUtility.runtime_checks(self.root)
      finally:
         self.root.register = real_register

   # ------------------------------------------------------------------ #
   # threading contract                                                   #
   # ------------------------------------------------------------------ #

   def test_worker_thread_to_tk_via_queue_and_after(self):
      msg_queue = queue.Queue()
      delivered = []
      done = threading.Event()
      timed_out = {"value": False}

      def drain_queue_on_main_thread():
         try:
            while True:
               item = msg_queue.get_nowait()
               delivered.append(item)
               if item == "ok":
                  done.set()
         except queue.Empty:
            pass

         if done.is_set():
            self.root.quit()
         else:
            self.root.after(10, drain_queue_on_main_thread)

      def worker_thread_fn():
         # Worker thread must not call Tk APIs directly.
         msg_queue.put("ok")

      self.root.after(0, drain_queue_on_main_thread)
      threading.Thread(target=worker_thread_fn, daemon=True).start()
      self.root.after(1000, lambda: (timed_out.__setitem__("value", True), self.root.quit()))
      self.root.mainloop()

      self.assertFalse(timed_out["value"], "Timed out waiting for worker to main-thread delivery")
      self.assertEqual(delivered, ["ok"])


if __name__ == "__main__":
   unittest.main()
