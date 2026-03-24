from __future__ import annotations
import tkinter as tk

from devtools.constants import CommonGeometryOption, GeometryType, GridGeometryOption, PackGeometryOptionName, PlaceGeometryOption
from devtools.utils import Utils


class TreeViewUtils:
	@staticmethod
	def _safe_int(value, default=0) -> int:
		try:
			return int(value)
		except (TypeError, ValueError):
			return default

	@staticmethod
	def check_sibling_geometry_type(widget) -> GeometryType | None:
		siblings = widget.master.winfo_children()

		for sibling in siblings:
			if sibling == widget:
				continue
			geo_manager = Utils.build_widget_geometry_manager_info(sibling)
			geometry_type = getattr(geo_manager, 'geometry_type', None)

			if geometry_type in (GeometryType.PACK, GeometryType.GRID, GeometryType.PLACE):
				return geometry_type

	@staticmethod
	def _nearest_grid_sibling_positions(widget: tk.Widget):
		parent = widget.master
		if parent is None:
			return None, None

		siblings = list(parent.winfo_children())
		if widget not in siblings:
			return None, None

		index = siblings.index(widget)

		def to_grid_pos(target_widget: tk.Widget):
			try:
				info = target_widget.grid_info()
				row = TreeViewUtils._safe_int(info.get("row"), 0)
				column = TreeViewUtils._safe_int(info.get("column"), 0)
				return row, column
			except Exception:
				return None

		prev_grid = None
		for sibling in reversed(siblings[:index]):
			if sibling.winfo_ismapped() and sibling.winfo_manager() == GeometryType.GRID.value:
				prev_grid = to_grid_pos(sibling)
				if prev_grid is not None:
					break

		next_grid = None
		for sibling in siblings[index + 1:]:
			if sibling.winfo_ismapped() and sibling.winfo_manager() == GeometryType.GRID.value:
				next_grid = to_grid_pos(sibling)
				if next_grid is not None:
					break

		return prev_grid, next_grid

	@staticmethod
	def infer_geometry_options(widget: tk.Widget, geometry_type: GeometryType) -> dict:
		parent = widget.master
		if parent is None:
			return {}

		if geometry_type == GeometryType.GRID:
			prev_grid, next_grid = TreeViewUtils._nearest_grid_sibling_positions(widget)

			if prev_grid and next_grid:
				prev_row, prev_col = prev_grid
				next_row, next_col = next_grid
				if next_col > 0:
					return {"row": next_row, "column": next_col - 1}
				if prev_row == next_row and next_col - prev_col > 1:
					return {"row": prev_row, "column": prev_col + 1}
				if prev_col < next_col:
					return {"row": prev_row, "column": prev_col + 1}
				return {"row": next_row, "column": 0}

			if next_grid:
				next_row, next_col = next_grid
				if next_col > 0:
					return {"row": next_row, "column": next_col - 1}
				return {"row": max(0, next_row - 1), "column": 0}

			if prev_grid:
				prev_row, prev_col = prev_grid
				return {"row": prev_row, "column": prev_col + 1}

			return {"row": 0, "column": 0}

		if geometry_type == GeometryType.PACK:
			siblings = list(parent.winfo_children())
			if widget in siblings:
				index = siblings.index(widget)
				for sibling in siblings[index + 1:]:
					if sibling.winfo_ismapped() and sibling.winfo_manager() == GeometryType.PACK.value:
						return {"before": sibling}
			return {}

		return {}

	@staticmethod
	def _default_geometry_state_for_type(geometry_type: GeometryType) -> dict:
		match geometry_type:
			case GeometryType.GRID:
				keys = Utils.extract_class_attributes(GridGeometryOption)
			case GeometryType.PACK:
				keys = Utils.extract_class_attributes(PackGeometryOptionName)
			case GeometryType.PLACE:
				keys = Utils.extract_class_attributes(PlaceGeometryOption)
			case _:
				keys = [CommonGeometryOption.GEOMETRY_TYPE, CommonGeometryOption.VISIBILITY]

		state = {key: 0 for key in keys}
		state[CommonGeometryOption.GEOMETRY_TYPE] = geometry_type.value
		state[CommonGeometryOption.VISIBILITY] = True
		return state

	@staticmethod
	def build_geometry_state_for_widget(widget: tk.Widget, geometry_type: GeometryType) -> dict:
		state = TreeViewUtils._default_geometry_state_for_type(geometry_type)

		try:
			if geometry_type == GeometryType.GRID and widget.winfo_manager() == GeometryType.GRID.value:
				for key, value in widget.grid_info().items():
					if key in state:
						state[key] = value
			elif geometry_type == GeometryType.PACK and widget.winfo_manager() == GeometryType.PACK.value:
				for key, value in widget.pack_info().items():
					if key in state:
						state[key] = value
			elif geometry_type == GeometryType.PLACE and widget.winfo_manager() == GeometryType.PLACE.value:
				for key, value in widget.place_info().items():
					if key in state:
						state[key] = value
		except Exception:
			pass

		state[CommonGeometryOption.GEOMETRY_TYPE] = geometry_type.value
		state[CommonGeometryOption.VISIBILITY] = widget.winfo_ismapped()
		return state
