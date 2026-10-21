from __future__ import annotations
from abc import ABC, abstractmethod

from uniserde import ObjectId

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence, WorkbookPersistence
from ..data_utils.xlsx_generator import XlsxGenerator


class WorkbookPageBase(rio.Component):
    param_id: str = ""
    
    _banner_factory: comps.BannerFactory = comps.BannerFactory()
    _workbook: data_models.Template | None = None
    _fields: list[data_models.Field] = []
    _field_selection: dict[ObjectId, bool] = {}
    _all_dropdown_selections: dict[ObjectId, dict[str, bool]] = {}

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def get_workbook_persistence(self) -> WorkbookPersistence:
        pass

    @abstractmethod
    def build(self) -> rio.Component:
        pass

    def unpack_dataclass(self):
        self._fields = self._workbook.fields
        self._field_selection = self._workbook.get_field_selection_dict()
        self._all_dropdown_selections = self._workbook.get_all_dropdown_selections_dict()
    
    def pack_dataclass(self):
        self._workbook.fields = self._fields
        self._workbook.set_field_selection_from_dict(self._field_selection)
        self._workbook.set_field_value_selection_from_dict(self._all_dropdown_selections)

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self._banner_factory = comps.BannerFactory(self.get_title())
        self._workbook = await self.get_workbook_persistence().find_one_by_id(self.param_id)
        if self._workbook is None:
            self.session.navigate_to("/")
            return
        
        self.unpack_dataclass()

    async def _on_save_button_press(self) -> None:
        self.pack_dataclass()
        await self.get_workbook_persistence().upsert_one(self._workbook)
        self._banner_factory.update(
            parent=self,
            name=self._workbook.name,
            status='success',
        )
    
    async def _on_save_as_button_press(self) -> None:
        new_item = await comps.SaveDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"Save {self.get_title()} As...",
            item=data_models.DialogItem(self._workbook.name),
        )
        result = await comps.SaveDialog.check_name_and_update_status(
            item=new_item,
            persistence=self.get_workbook_persistence(),
            banner_factory=self._banner_factory,
            parent=self
        )
        if result:
            self.pack_dataclass()
            new_workbook = self._workbook.copy()
            new_workbook.name = new_item.name
            await self.get_workbook_persistence().insert_one(new_workbook)
            self._banner_factory.update(
                parent=self,
                name=new_item.name,
                status='success',
            )

    async def _on_update_fields_button_press(self) -> None:
        fields = await self.session[Persistence].get_field().get_all(self.session[data_models.AppUser])
        self._workbook.update_fields(fields)
        self.unpack_dataclass()
        self._banner_factory.update(
            parent=self,
            status='updated',
            title='Fields',
        )


@rio.page(
    name="Workbook",
    url_segment="workbooks/{param_id}",
    guard=auth.guard,
)
class WorkbookPage(WorkbookPageBase):

    def get_title(self) -> str:
        return "Workbook"

    def get_workbook_persistence(self) -> WorkbookPersistence:
        return self.session[Persistence].get_workbook()

    async def _on_save_as_template_button_press(self) -> None:
        new_item = await comps.SaveDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"Save As Template...",
            item=data_models.DialogItem(self._workbook.name),
        )
        result = await comps.SaveDialog.check_name_and_update_status(
            item=new_item,
            persistence=self.session[Persistence].get_template(),
            banner_factory=self._banner_factory,
            parent=self,
            title="Template",
        )
        if result:
            self.pack_dataclass()
            template = data_models.Template.new_from_workbook(self._workbook)
            template.name = new_item.name
            await self.session[Persistence].get_template().insert_one(template)
            self._banner_factory.update(
                parent=self,
                name=new_item.name,
                status='success',
                title="Template",
            )
    
    async def _on_download_workbook_button_press(self) -> None:
        self.pack_dataclass()
        await self.get_workbook_persistence().upsert_one(self._workbook)
        self.session.navigate_to(f"/download/{self.param_id}")

    async def _on_download_qr_button_press(self) -> None:
        self.pack_dataclass()
        await self.get_workbook_persistence().upsert_one(self._workbook)
        xlsx_data = XlsxGenerator.generate_qr(
            workbook=self._workbook,
        )
        await self.session.save_file(
            file_contents=xlsx_data.getvalue(),
            file_name=f"{self._workbook.name}_QRCode.xlsx",
        )

    def build(self) -> rio.Component:
        if self._workbook is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )
        
        return rio.Column(
            comps.TitleBar(
                page_name=f"Workbook: {self._workbook.name}",
                buttons=[
                    comps.Button(
                        "Save Workbook",
                        on_press=self._on_save_button_press,
                    ),
                    comps.Button(
                        "Save Workbook As...",
                        on_press=self._on_save_as_button_press,
                    ),
                    comps.Button(
                        "Save As Template...",
                        on_press=self._on_save_as_template_button_press,
                    ),
                    comps.Button(
                        "Update Fields",
                        on_press=self._on_update_fields_button_press,
                    ),
                ],
                buttons_rhs=[
                    comps.Button(
                        "Download Workbook",
                        on_press=self._on_download_workbook_button_press,
                    ),
                    comps.Button(
                        "Download QRCode",
                        on_press=self._on_download_qr_button_press,
                    ),
                ]
            ),
            comps.FilteredFieldSelectionTable(
                fields=self.bind()._fields,
                field_selection=self.bind()._field_selection,
                all_dropdown_selections=self.bind()._all_dropdown_selections,
                grow_y=True,
            ),            
            self._banner_factory.build(),
        )