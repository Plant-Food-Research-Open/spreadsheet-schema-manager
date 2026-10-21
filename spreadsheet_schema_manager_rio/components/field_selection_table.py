from collections.abc import Callable
from collections import Counter

import rio
import functools

from uniserde import ObjectId

from .. import components as comps
from .. import constants, data_models
from .table_filter import FilterRow
from .field_table import FilteredFieldBase


class FieldSelectionTable(comps.CustomTable[data_models.Field]):
    field_selection: dict[ObjectId, bool] = {}
    all_dropdown_selections: dict[ObjectId, dict[str, bool]] = {}

    def __post_init__(self) -> None:
        self.min_widths = [0, 0, 0, 10, 0, 0, 15]
        self.column_spacing = 0.8
    
    def checkbox_on_change(self, field_id: ObjectId, event: rio.CheckboxChangeEvent) -> None:
        self.field_selection[field_id] = event.is_on

    def build_header(self) -> list[rio.Component]:
        return [
            rio.Text(""),
            rio.Row(comps.BoldText("Group")),
            rio.Row(comps.BoldText("Type")),
            rio.Row(comps.BoldText("Field")),
            rio.Row(comps.BoldText("Selected Values")),
            rio.Row(comps.BoldText("Reference URL")),
            rio.Row(comps.BoldText("Description")),
        ]

    def build_row(self, field: data_models.Field) -> list[rio.Component]:
        output = [
            rio.Checkbox(
                self.field_selection[field.id],
                on_change=functools.partial(self.checkbox_on_change, field.id),
            ),
            rio.Text(field.group),
            rio.Text(field.__class__.__name__),
            rio.Link(
                rio.Text(
                    field.header,
                    fill=self.session.theme.secondary_color,
                    underlined=True,
                    overflow='ellipsize',
                ),
                f"/fields/{str(field.id)}",
            ),
        ]

        if isinstance(field, data_models.Category):
            output.append(
                comps.CustomDropdown(
                    options=self.all_dropdown_selections.get(field.id),
                    label="",
                )
            )
        else:
            output.append(rio.Text(""))

        if field.ref == "":
            output.append(
                rio.Text("N/A")
            )
        else:
            output.append(
                rio.Link(
                    "Link",
                    field.ref,
                    open_in_new_tab=True,
                    align_x=0,
                )
            )
        
        output.append(
            rio.Text(
                field.desc,
                overflow='ellipsize',
            )
        )

        return output


class FilteredFieldSelectionTable(FilteredFieldBase):
    field_selection: dict[ObjectId, bool] = {}
    all_dropdown_selections: dict[ObjectId, dict[str, bool]] = {}

    @rio.event.on_populate
    def on_populate(self) -> None:
        selected_group_counter = Counter(self._option_map.get(field.group, field.group) for field in self.fields if self.field_selection.get(field.id, False))
        selected_type_counter = Counter(field.__class__.__name__ for field in self.fields if self.field_selection.get(field.id, False))
        for option in self._group_options:
            option.subname = f"({selected_group_counter.get(option.name, 0)}/{self._group_counter.get(option.name, 0)})"
        for option in self._type_options:
            option.subname = f"({selected_type_counter.get(option.name, 0)}/{self._type_counter.get(option.name, 0)})"

    def build(self) -> rio.Component:
        fields_filtered = self.filter_fields()

        return rio.Column(
            FilterRow(
                group_options=self._group_options,
                type_options=self._type_options,
                on_change_status=self.on_change_selection,
            ),
            rio.ScrollContainer(
                rio.Column(
                    FieldSelectionTable(
                        rows=fields_filtered,
                        field_selection=self.field_selection,
                        all_dropdown_selections=self.all_dropdown_selections,
                        grow_y=True,
                    ),
                    spacing=0.5,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
        )
