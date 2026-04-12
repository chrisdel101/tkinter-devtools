from __future__ import annotations

from devtools.constants import CommonGeometryOption


class ConfigListboxUtilsMixin:

    @staticmethod
    def _to_bool(value) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")

    @staticmethod
    def _visibility_display_bool(value) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return "true" if int(value) != 0 else "false"
        value_str = str(value).strip().lower()
        return "true" if value_str in ("1", "true", "yes", "on") else "false"

    @staticmethod
    def _normalize_bool_dropdown_values(key_entry_value: str, option_values: list) -> list:
        # Convert a value to its canonical boolean string representation in the UI
        if key_entry_value in (CommonGeometryOption.VISIBILITY, "expand"):
            return ["true", "false"]
        return option_values

    @staticmethod
    def _get_index_from_event_coords(index, event) -> int:
        # use event x and y w tk index - get listbox item index
        return index(f"@{event.x},{event.y}")
