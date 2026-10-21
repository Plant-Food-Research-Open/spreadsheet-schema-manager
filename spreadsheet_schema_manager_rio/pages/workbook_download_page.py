from __future__ import annotations

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence, WorkbookPersistence
from ..data_utils.xlsx_generator import XlsxGenerator


@rio.page(
    name="WorkbookDownload",
    url_segment="download/{param_id}",
    guard=auth.guard,
)
class WorkbookDownloadPage(rio.Component):
    param_id: str = ""

    _workbook: data_models.Template | None = None
    _fields_in_order: list[data_models.Field] | None = None
    _download_button_loading: bool = False

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self._workbook = await self.get_workbook_persistence().find_one_by_id(self.param_id)
        if self._workbook is None:
            self.session.navigate_to("/")
            return
        
        # Prepare self._fields_in_order
        # Start with self._workbook.field_order, modify into newly selected fields, and retain any original order
        selected_fields = [field_id for field_id, value in self._workbook.get_field_selection_dict().items() if value]
        selected_field_set = set(selected_fields)
        fields_in_order = self._workbook.field_order.copy()
        fields_in_order[:] = [field_id for field_id in fields_in_order if field_id in selected_field_set]
        _fields_in_order_set = set(fields_in_order)
        fields_in_order.extend([field_id for field_id in selected_fields if field_id not in _fields_in_order_set])
        fields_dict = self._workbook.get_fields_dict()
        self._fields_in_order = [fields_dict[field_id] for field_id in fields_in_order]
 
    def get_workbook_persistence(self) -> WorkbookPersistence:
        return self.session[Persistence].get_workbook()

    async def _on_download_button_press(self) -> None:
        self._download_button_loading = True

        self._workbook.field_order = [field.id for field in self._fields_in_order]
        await self.get_workbook_persistence().upsert_one(self._workbook)
        user = self.session[data_models.AppUser]
        xlsx_data = XlsxGenerator.generate_workbook(
            workbook=self._workbook,
            date_format=user.date_format,
            include_constant_category=user.include_constant_category,
        )

        await self.session.save_file(
            file_contents=xlsx_data.getvalue(),
            file_name=f"{self._workbook.name}.xlsx",
        )

        self._download_button_loading = False
    
    def build(self) -> rio.Component:
        if self._fields_in_order is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )
        
        return rio.Column(
            comps.TitleBar(
                page_name=f"Download Workbook: {self._workbook.name}",
                buttons=[
                    rio.Link(
                        comps.Button(
                            "Back",
                        ),
                        f"/workbooks/{self.param_id}",
                        # align_x=0,
                    ),
                    comps.Button(
                        "Download",
                        on_press=self._on_download_button_press,
                        is_loading=self._download_button_loading,
                    ),
                ],
            ),
            rio.ScrollContainer(
                rio.Column(
                    rio.Text("Arrange Field Order", font_size=1.5, font_weight="bold", margin_top=1),
                    comps.ReorderableFieldList(
                        fields=self.bind()._fields_in_order,
                        margin=constants.PAGE_MARGIN_X,
                        grow_y=True,
                    ),
                    spacing=0.5,
                    align_x=0,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_x=True,
                grow_y=True,
            ),            
        )