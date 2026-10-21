from collections.abc import Callable

import rio
import functools
from bson import ObjectId

from .. import components as comps
from .. import constants, data_models
from ..data_models import DatasetStatus
from .table_filter import AddNewRow


class DatasetTable(comps.CustomTable[data_models.Dataset]):
    on_download_raw_button_press: Callable[[ObjectId], None] = lambda: None
    on_download_standardised_button_press: Callable[[ObjectId], None] = lambda: None
    on_delete_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_rename_button_press: Callable[[ObjectId, str], None] = lambda: None

    def __post_init__(self) -> None:
        self.min_widths = [0, 15, 0, 0, 0, 13]
        self.column_spacing = 1
    
    def build_header(self) -> list[rio.Component]:
        return [
            rio.Row(comps.BoldText("Status")),
            rio.Row(comps.BoldText("Name")),
            rio.Row(comps.BoldText("Raw Data")),
            rio.Row(comps.BoldText("Standardise")),
            rio.Row(comps.BoldText("Standardised Data")),
            rio.Row(comps.BoldText("Actions")),
        ]

    def build_row(self, row: data_models.Dataset) -> list[rio.Component]:
        output = [
            comps.ColoredStatus(row.status),
            rio.Text(
                row.name,
                align_x=0,
            )
        ]
        
        buttons = [
            rio.Link(
                comps.Button(
                    "View",
                    style="minor",
                    accessibility_label=f"View {row.name}",
                ),
                f"/datasets/{str(row.id)}?content=raw",
                align_x=0,
            ),
            comps.Button(
                "Download",
                on_press=functools.partial(self.on_download_raw_button_press, row.id),
                style="minor",
                accessibility_label=f"Download {row.name}",
            )
        ]
        output.append(
            rio.Row(
                *buttons,
                spacing=0.5,
                align_x=0,
            )
        )

        if row.status in (DatasetStatus.WARNING, DatasetStatus.READY, DatasetStatus.COMPLETE):
            output.append(
                rio.Link(
                    comps.Button(
                        "Run",
                        style="minor",
                        align_x=0,
                        accessibility_label=f"Run {row.name}",
                    ),
                    f"/standardise/{str(row.id)}",
                    align_x=0,
                )
            )
        else:
            output.append(
                comps.Button(
                    "Run",
                    style="minor",
                    align_x=0,
                    is_sensitive=False,
                    accessibility_label=f"Run {row.name}",
                )
            )

        buttons = []
        if row.status == DatasetStatus.COMPLETE:
            buttons.append(
                rio.Link(
                    comps.Button(
                        "View",
                        style="minor",
                        accessibility_label=f"View standardised {row.name}",
                    ),
                    f"/datasets/{str(row.id)}?content=standardised",
                    align_x=0,
                ),
            )
        else:
            buttons.append(
                comps.Button(
                    "View",
                    style="minor",
                    is_sensitive=False,
                    accessibility_label=f"View standardised {row.name}",
                ),
            )

        buttons.append(
            comps.Button(
                "Download",
                on_press=functools.partial(self.on_download_standardised_button_press, row.id),
                style="minor",
                is_sensitive=(row.status == DatasetStatus.COMPLETE),
                accessibility_label=f"Download standardised {row.name}",
            )
        )
        
        output.append(
            rio.Row(
                *buttons,
                spacing=0.5,
                align_x=0,
            )
        )

        buttons = [
            comps.Button(
                "Rename",
                on_press=functools.partial(self.on_rename_button_press, row.id, row.name),
                style="minor",
                accessibility_label=f"Rename {row.name}",
            )
        ]
        output.append(
            rio.Row(
                *buttons,
                rio.Spacer(),
                rio.IconButton(
                    "material/delete",
                    min_size=constants.ICON_BUTTON_SIZE,
                    margin_right=0.5,
                    color="danger",
                    on_press=functools.partial(self.on_delete_button_press, row.id, row.name),
                    accessibility_label=f"Delete {row.name}",
                ),
            )
        )

        return output


class FilteredDatasetTable(rio.Component):
    datasets: list[data_models.Dataset] = []
    on_new_button_press: Callable[[], None] = lambda: None
    on_download_raw_button_press: Callable[[ObjectId], None] = lambda: None
    on_download_standardised_button_press: Callable[[ObjectId], None] = lambda: None
    on_delete_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_rename_button_press: Callable[[ObjectId, str], None] = lambda: None
    add_button_label: str = "Add dataset"

    def build(self) -> rio.Component:
        return rio.Column(
            AddNewRow(
                on_new_button_press=self.on_new_button_press,
                add_button_label=self.add_button_label,
            ),
            rio.ScrollContainer(
                rio.Column(
                    DatasetTable(
                        rows=self.datasets,
                        on_download_raw_button_press=self.on_download_raw_button_press,
                        on_download_standardised_button_press=self.on_download_standardised_button_press,
                        on_delete_button_press=self.on_delete_button_press,
                        on_rename_button_press=self.on_rename_button_press,
                        align_y=0,
                    ),
                    spacing=0.5,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
        )