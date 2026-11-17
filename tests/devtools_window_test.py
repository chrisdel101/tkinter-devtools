import unittest

from src.DevtoolsWindow import DevtoolsWindow
from src.style import Style

_DEFAULTS = Style.devtools_window


class DevtoolsWindowTests(unittest.TestCase):
    def test_build_window_geometry_uses_style_defaults_without_kwargs(self):
        self.assertEqual(
            DevtoolsWindow._build_window_geometry(),
            f"{_DEFAULTS['default_width']}x{_DEFAULTS['default_height']}"
            f"+{_DEFAULTS['default_x_coord']}+{_DEFAULTS['default_y_coord']}",
        )

    def test_build_window_geometry_uses_all_kwargs(self):
        self.assertEqual(
            DevtoolsWindow._build_window_geometry(width=400, height=300, x_coord=100, y_coord=80),
            "400x300+100+80",
        )

    def test_build_window_geometry_fills_missing_kwargs_with_style_defaults(self):
        self.assertEqual(
            DevtoolsWindow._build_window_geometry(width=400, y_coord=50),
            f"400x{_DEFAULTS['default_height']}+{_DEFAULTS['default_x_coord']}+50",
        )


if __name__ == "__main__":
    unittest.main()
