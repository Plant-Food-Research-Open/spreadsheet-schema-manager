from typing import Type
import rio
import functools

from uniserde import ObjectId

from .. import components as comps
from .. import constants, data_models
from ..data_models import StandardisationSwitch


ROW_WIDTHS = [15]


class StandardiseValueTable(comps.CustomTable[str]):
    field_values: list[data_models.Row] = []
    text_switch_selections: dict[str, StandardisationSwitch] = {}
    text_value_selections: dict[str, data_models.Row] = {}
    new_text_values: dict[str, str] = {}

    _field_value_options: dict[str, data_models.Row] = {}

    def __post_init__(self) -> None:
        self.min_widths = [15]
        self._field_value_options = {row.header: row for row in self.field_values}

    def on_switch_change(self, value: str, event: rio.SwitcherBarChangeEvent) -> None:
        self.text_switch_selections[value] = event.value
        self.force_refresh()

    def on_value_selection_change(self, value: str, event: rio.DropdownChangeEvent) -> None:
        self.text_value_selections[value] = event.value
    
    def on_text_change(self, value: str, event: rio.TextInputChangeEvent) -> None:
        self.new_text_values[value] = event.text
    
    def build_header(self) -> list[rio.Component]:
        output = [rio.Row(comps.BoldText("Value"), margin_x=0.5)]
        if self.field_values:
            output.append(comps.BoldText("Map to an existing value...", align_x=0.5, margin_x=0.5))
            output.append(comps.BoldText("Or", align_x=0.5, margin_x=0.5))
        
        output.append(comps.BoldText("Add as a new value...", align_x=0.5, margin_x=0.5))
        return output

    def build_row(self, row: str) -> list[rio.Component]:
        output = [rio.Row(rio.Text(row), margin_x=0.5)]
        if self.field_values:
            output.append(
                rio.Dropdown(
                    options=self._field_value_options,
                    selected_value=self.text_value_selections.get(row),
                    is_sensitive=(self.text_switch_selections.get(row) == StandardisationSwitch.EXISTING),
                    on_change=functools.partial(self.on_value_selection_change, row),
                )
            )
            output.append(
                rio.SwitcherBar(
                    rio.SwitcherBarItem(StandardisationSwitch.EXISTING, StandardisationSwitch.EXISTING.name.title()),
                    rio.SwitcherBarItem(StandardisationSwitch.NEW, StandardisationSwitch.NEW.name.title()),
                    selected_value=self.text_switch_selections.get(row),
                    on_change=functools.partial(self.on_switch_change, row),
                    align_x=0.5,
                )
            )

        output.append(
            rio.TextInput(
                text=self.new_text_values.get(row) if (self.text_switch_selections.get(row) == StandardisationSwitch.NEW) else "",
                is_sensitive=(self.text_switch_selections.get(row) == StandardisationSwitch.NEW),
                on_change=functools.partial(self.on_text_change, row),
                accessibility_label=f"New value for {row}",
            )
        )
        return output
