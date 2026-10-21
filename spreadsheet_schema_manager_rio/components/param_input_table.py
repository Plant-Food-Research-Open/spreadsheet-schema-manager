from collections.abc import Callable

import rio
import functools

from .. import components as comps
from .. import constants, data_models
from .table_filter import AddNewRow


class ParamInputTable(comps.CustomTable[data_models.ParamValue]):
    on_delete_button_press: Callable[[int], None] = lambda: None

    def __post_init__(self) -> None:
        self.min_widths = [10, 18, 0]

    def build_header(self) -> list[rio.Component]:
        return [
            rio.Row(comps.BoldText("Parameter")),
            rio.Row(comps.BoldText("Value")),
            rio.Row(),
        ]

    def build_row(self, pv: data_models.ParamValue) -> list[rio.Component]:
        index = self.rows.index(pv)

        def on_param_change(event: rio.TextInputChangeEvent):
            pv.param = event.text

        def on_value_change(event: rio.TextInputChangeEvent):
            pv.value = event.text

        return [
            rio.TextInput(
                text=pv.param,
                on_change=on_param_change,
                accessibility_label="Parameter",
            ),
            rio.TextInput(
                text=pv.value,
                on_change=on_value_change,
                accessibility_label="Value",
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


class FilteredParamInputTable(rio.Component):
    field: data_models.Field
    dummy: int = -1
            
    def _on_new_button_press(self) -> None:
        self.field.params.append(data_models.ParamValue())
        self.dummy = len(self.field.params)
        self.field.params = self.field.params

    def _on_delete_button_press(self, index: int) -> None:
        del self.field.params[index]
        self.dummy = len(self.field.params)

    def build(self) -> rio.Component:
        return rio.Column(
            AddNewRow(
                on_new_button_press=self._on_new_button_press,
            ),
            rio.ScrollContainer(
                rio.Column(
                    ParamInputTable(
                        key=self.dummy,
                        rows=self.field.params,
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
    