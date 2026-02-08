from dataclasses import dataclass
import tkinter as tk

from devtools.constants import GeometryType

# stores the winfo_manager 
@dataclass(frozen=True)
class GeometryManagerInfo: 
    geometry_type: GeometryType  # winfo_manager() value
    geometry_options: dict # pack, grid, or place info dict. emptry type uses {}
    name: str | None = None  # optional name