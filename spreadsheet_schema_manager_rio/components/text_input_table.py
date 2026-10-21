from collections.abc import Callable

import rio
import functools

from .. import components as comps
from .. import constants, data_models
from .table_filter import AddNewRow


class TextInputTable(comps.CustomTable[data_models.Row]):
    on_delete_button_press: Callable[[int], None] = lambda: None

    def __post_init__(self) -> None:
        self.min_widths = [10, 18, 0]

    def build_header(self) -> list[rio.Component]:
        return [
            rio.Row(comps.BoldText("Value Header")),
            rio.Row(comps.BoldText("Value Description")),
            rio.Row(),
        ]

    def build_row(self, row: data_models.Row) -> list[rio.Component]:
        index = self.rows.index(row)

        def on_header_value_change(event: rio.TextInputChangeEvent):
            row.header = event.text

        def on_desc_value_change(event: rio.TextInputChangeEvent):
            row.desc = event.text

        return [
            rio.TextInput(
                text=row.header,
                on_change=on_header_value_change,
                accessibility_label="Value Header",
            ),
            rio.TextInput(
                text=row.desc,
                on_change=on_desc_value_change,
                accessibility_label="Value Description",
            ),
            rio.Row(
                rio.IconButton(
                    "material/delete",
                    min_size=constants.ICON_BUTTON_SIZE,
                    margin_right=0.5,
                    color="danger",
                    on_press=functools.partial(self.on_delete_button_press, index),
                    accessibility_label=f"Delete row {index + 1}",
                ),
                spacing=0.5,
                margin_x=1,
                align_x=1,
            ),
        ]


class FilteredTextInputTable(rio.Component):
    field: data_models.Field
    dummy: int = -1

    def _on_new_button_press(self) -> None:
        self.field.values.append(data_models.Row())
        self.dummy = len(self.field.values)
        self.field.values = self.field.values

    def _on_delete_button_press(self, index: int) -> None:
        del self.field.values[index]
        self.dummy = len(self.field.values)

    def build(self) -> rio.Component:
        return rio.Column(
            AddNewRow(
                on_new_button_press=self._on_new_button_press,
            ),
            rio.ScrollContainer(
                rio.Column(
                    TextInputTable(
                        key=self.dummy,
                        rows=self.field.values,
                        on_delete_button_press=self._on_delete_button_press,
                        grow_y=True,
                    ),
                    spacing=0.5,
                    align_y=0,
                ),
                margin_y=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
            grow_y=True,
        )
    