from dataclasses import dataclass
import tkinter as tk

from devtools.constants import GeometryType

# stores the winfo_manager 
@dataclass(frozen=True)
class GeometryManagerInfo: 
    geometry_type: GeometryType  # winfo_manager() value
    geometry_type_info: dict # pack, grid, or place info dict