from collections.abc import Callable

import rio
import functools
from bson import ObjectId

from .. import components as comps
from .. import constants, data_models
from .table_filter import AddNewRow


class WorkbookTable(comps.CustomTable[data_models.Template]):
    is_template: bool = False
    on_delete_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_rename_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_download_workbook_button_press: Callable[[ObjectId], None] = lambda: None
    on_download_qr_button_press: Callable[[ObjectId], None] = lambda: None
    on_new_workbook_button_press: Callable[[ObjectId, str], None] = lambda: None

    def __post_init__(self) -> None:
        if self.is_template:
            self.min_widths = [16, 0]
        else:
            self.min_widths = [10, 6, 0]

    def build_header(self) -> list[rio.Component]:
        output = []
        
        if self.is_template:
            output.append(rio.Row(comps.BoldText("Template Name")))
        else:
            output.append(rio.Row(comps.BoldText("Workbook Name")))

        if not self.is_template:
            output.append(rio.Row(comps.BoldText("Template Name")))

        output.append(rio.Row(comps.BoldText("Actions")))
        return output

    def build_row(self, workbook: data_models.Template) -> list[rio.Component]:
        output = [
            rio.Row(
                rio.Link(
                    workbook.name,
                    f"/{"templates" if self.is_template else "workbooks"}/{workbook.id}",
                    align_x=0,
                )
            )
        ]

        if not self.is_template:
            output.append(
                rio.Row(
                    rio.Link(
                        workbook.template_name,
                        f"/templates/{str(workbook.template_id)}",
                        align_x=0,
                    )
                )
            )

        buttons = []
        if self.is_template:
            buttons = [
                comps.Button(
                    "New Workbook",
                    on_press=functools.partial(self.on_new_workbook_button_press, workbook.id, workbook.name),
                    style="minor",
                    accessibility_label=f"Create new workbook from {workbook.name}",
                ),
            ]
        else:
            buttons = [
                comps.Button(
                    "Download Workbook",
                    on_press=functools.partial(self.on_download_workbook_button_press, workbook.id),
                    style="minor",
                    accessibility_label=f"Download {workbook.name}",
                ),
                comps.Button(
                    "Download QRCode",
                    on_press=functools.partial(self.on_download_qr_button_press, workbook.id),
                    style="minor",
                    accessibility_label=f"Download QR code for {workbook.name}",
                ),
            ]

        buttons.append(
            comps.Button(
                "Rename",
                on_press=functools.partial(self.on_rename_button_press, workbook.id, workbook.name),
                style="minor",
                accessibility_label=f"Rename {workbook.name}",
            )
        )

        output.append(
            rio.Row(
                *buttons,
                rio.Spacer(),
                rio.IconButton(
                    "material/delete",
                    min_size=constants.ICON_BUTTON_SIZE,
                    margin_right=0.5,
                    color="danger",
                    on_press=functools.partial(self.on_delete_button_press, workbook.id, workbook.name),
                    accessibility_label=f"Delete {workbook.name}",
                ),
                spacing=0.5,
            )
        )

        return output


class FilteredWorkbookTable(rio.Component):
    is_template: bool = False
    workbooks: list[data_models.Template] = []
    on_new_button_press: Callable[[], None] = lambda: None
    on_delete_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_rename_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_download_workbook_button_press: Callable[[ObjectId], None] = lambda: None
    on_download_qr_button_press: Callable[[ObjectId], None] = lambda: None
    on_new_workbook_button_press: Callable[[ObjectId, str], None] = lambda: None
    add_button_label: str = "Add item"

    def build(self) -> rio.Component:
        return rio.Column(
            AddNewRow(
                on_new_button_press=self.on_new_button_press,
                add_button_label=self.add_button_label,
            ),
            rio.ScrollContainer(
                rio.Column(
                    WorkbookTable(
                        rows=self.workbooks,
                        is_template=self.is_template,
                        on_delete_button_press=self.on_delete_button_press,
                        on_rename_button_press=self.on_rename_button_press,
                        on_download_workbook_button_press=self.on_download_workbook_button_press,
                        on_download_qr_button_press=self.on_download_qr_button_press,
                        on_new_workbook_button_press=self.on_new_workbook_button_press,
                        grow_y=True,
                    ),
                    spacing=0.5,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
        )