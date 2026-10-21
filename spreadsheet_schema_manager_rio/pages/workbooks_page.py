from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type

from bson import ObjectId

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence, WorkbookPersistence
from ..data_utils.xlsx_generator import XlsxGenerator


class WorkbooksPageBase(rio.Component):
    workbooks: list[data_models.Template] = []
    
    _banner_factory: comps.BannerFactory = comps.BannerFactory()
    _fields: list[data_models.Field] = []

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def get_type(self) -> Type[data_models.Template]:
        pass

    @abstractmethod
    def get_persistence(self) -> WorkbookPersistence:
        pass

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self.workbooks = await self.get_persistence().get_all(self.session[data_models.AppUser])
        self._banner_factory = comps.BannerFactory(self.get_type().__name__)
        self._fields = await self.session[Persistence].get_field().get_all(self.session[data_models.AppUser])

    async def _on_new_button_press(self) -> None:
        new_item = await comps.SaveDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"New {self.get_type().__name__}",
            item=data_models.DialogItem(),
        )

        result = await comps.SaveDialog.check_name_and_update_status(
            item=new_item,
            persistence=self.get_persistence(),
            banner_factory=self._banner_factory,
            parent=self
        )
        if result:
            workbook = self.get_type().new_empty(self.session[data_models.AppUser], self._fields)
            workbook.name = new_item.name
            await self.get_persistence().insert_one(workbook)
            await self.on_populate()
            self._banner_factory.update(
                parent=self,
                status='created',
                name=new_item.name,
            )

    async def _on_delete_button_press(self, id: ObjectId, name: str) -> None:
        selected_value = await self.session.show_yes_no_dialog(
            title=f"Delete {self.get_type().__name__}",
            text=f"Are you sure you want to delete {name}?",
        )
        if selected_value:
            await self.get_persistence().delete_one(id)
            await self.on_populate()
            self._banner_factory.update(
                parent=self,
                status='deleted',
                name=name,
            )

    async def _on_rename_button_press(self, id: ObjectId, name: str) -> None:
        new_item = await comps.SaveDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"Rename {self.get_type().__name__}",
            item=data_models.DialogItem(name),
        )
        result = await comps.SaveDialog.check_name_and_update_status(
            item=new_item,
            persistence=self.get_persistence(),
            banner_factory=self._banner_factory,
            parent=self
        )
        if result:
            await self.get_persistence().update_one_name(id, new_item.name)
            await self.on_populate()
            self._banner_factory.update(
                parent=self,
                status='renamed',
                name=new_item.name,
            )
    
    async def _on_download_workbook_button_press(self, id: ObjectId) -> None:
        self.session.navigate_to(f"/download/{id}")

    async def _on_download_qr_button_press(self, id: ObjectId) -> None:
        workbook = await self.get_persistence().get_one(id)
        xlsx_data = XlsxGenerator.generate_qr(
            workbook=workbook,
        )
        await self.session.save_file(
            file_contents=xlsx_data.getvalue(),
            file_name=f"{workbook.name}_QRCode.xlsx",
        )

    async def _on_new_workbook_button_press(self, template_id: ObjectId, template_name: str) -> None:
        template = await self.session[Persistence].get_template().get_one(template_id)
        new_item = await comps.SaveDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"New Workbook from {template_name}",
            item=data_models.DialogItem(),
        )

        result = await comps.SaveDialog.check_name_and_update_status(
            item=new_item,
            persistence=self.session[Persistence].get_workbook(),
            banner_factory=self._banner_factory,
            parent=self,
            title="Workbook",
        )
        if result:
            workbook = data_models.Workbook.new_from_template(self.session[data_models.AppUser], template)
            workbook.name = new_item.name
            id = await self.session[Persistence].get_workbook().insert_one(workbook)
            self.session.navigate_to(f"/workbooks/{str(id)}")

    
    def build(self) -> rio.Component:
        if self.workbooks is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )
        
        return rio.Column(
            comps.TitleBar(self.get_title()),
            comps.FilteredWorkbookTable(
                is_template=(self.get_type() == data_models.Template),
                workbooks=self.workbooks,
                on_new_button_press=self._on_new_button_press,
                on_delete_button_press=self._on_delete_button_press,
                on_rename_button_press=self._on_rename_button_press,
                on_download_workbook_button_press=self._on_download_workbook_button_press,
                on_download_qr_button_press=self._on_download_qr_button_press,
                on_new_workbook_button_press=self._on_new_workbook_button_press,
                add_button_label=f"Add {self.get_type().__name__.lower()}",
                grow_y=True,
            ),
            self._banner_factory.build(),
        )



@rio.page(
    name="Workbooks",
    url_segment="workbooks",
    guard=auth.guard,
)
class WorkbooksPage(WorkbooksPageBase):

    def get_title(self) -> str:
        team = self.session[data_models.AppUser].active_team
        if team is None:
            return "Workbooks (under your personal space)"
        else:
            return f"Workbooks (shared under team {team})"

    def get_type(self) -> Type[data_models.Template]:
        return data_models.Workbook

    def get_persistence(self) -> WorkbookPersistence:
        return self.session[Persistence].get_workbook()
