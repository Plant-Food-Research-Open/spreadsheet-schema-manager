from typing import Type
import rio
import functools

from .. import components as comps
from .. import constants, data_models
from ..data_models import StandardisationSwitch


class StandardiseFieldTable(comps.CustomTable[str]):
    fields: list[data_models.Field] = []
    all_switch_selections: dict[str, StandardisationSwitch] = {}
    all_field_selections: dict[str, data_models.Field] = {}
    all_field_errors: dict[str, bool] = {}
    all_type_selections: dict[str, Type[data_models.Field]] = {}

    _field_options: dict[str, data_models.Field] = {}

    def __post_init__(self) -> None:
        self.min_widths = [15]
        self._field_options = {f"{field.group} / {field.__class__.__name__} / {field.header}": field for field in self.fields}

    def on_switch_change(self, row: str, event: rio.SwitcherBarChangeEvent) -> None:
        self.all_switch_selections[row] = event.value
        self.force_refresh()

    def on_field_change(self, row: str, event: rio.DropdownChangeEvent) -> None:
        self.all_field_selections[row] = event.value
    
    def on_type_change(self, row: str, event: rio.DropdownChangeEvent) -> None:
        self.all_type_selections[row] = event.value
    
    def build_header(self) -> list[rio.Component]:
        output = [rio.Row(comps.BoldText("Header"), margin_x=0.5)]
        if self._field_options:
            output.append(rio.Row(comps.BoldText("Map to an existing Field...", align_x=0.5, margin_x=0.5)))
            output.append(rio.Row(comps.BoldText("Or", align_x=0.5, margin_x=0.5)))
        
        output.append(rio.Row(comps.BoldText("Add as a new Field of type...", align_x=0.5, margin_x=0.5)))
        return output

    def build_row(self, row: str) -> list[rio.Component]:
        output = [rio.Row(rio.Text(row), margin_x=0.5)]
        if self._field_options:
            output.append(
                rio.Rectangle(
                    content=rio.Dropdown(
                        options=self._field_options,
                        selected_value=self.all_field_selections.get(row),
                        is_sensitive = (self.all_switch_selections.get(row) == StandardisationSwitch.EXISTING),
                        on_change=functools.partial(self.on_field_change, row),
                    ),
                    stroke_width=0.1,
                    stroke_color=self.session.theme.danger_color if self.all_field_errors.get(row) else self.session.theme.background_color,
                )
            )
            output.append(
                rio.SwitcherBar(
                    rio.SwitcherBarItem(StandardisationSwitch.EXISTING, StandardisationSwitch.EXISTING.name.title()),
                    rio.SwitcherBarItem(StandardisationSwitch.NEW, StandardisationSwitch.NEW.name.title()),
                    selected_value=self.all_switch_selections.get(row),
                    on_change=functools.partial(self.on_switch_change, row),
                    align_x=0.5,
                )
            )
        
        output.append(
            rio.Dropdown(
                options=constants.FIELD_TYPE_DICT,
                selected_value=self.all_type_selections.get(row),
                is_sensitive = (self.all_switch_selections.get(row) == StandardisationSwitch.NEW),
                on_change=functools.partial(self.on_type_change, row),
            )
        )
        return output
