from __future__ import annotations

import pandas as pd
from bson import ObjectId
from collections import Counter

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence, FieldPersistence
from ..data_utils.df_reader import create_dialog_and_read_df
from ..data_utils.fields_serializer import FieldsSerializer
from ..data_utils.xlsx_generator import XlsxGenerator


@rio.page(
    name="Fields",
    url_segment="fields",
    guard=auth.guard,
)
class FieldsPage(rio.Component):
    page: int = 1

    # All page objects
    _banner_factory: comps.BannerFactory = comps.BannerFactory()

    # Page 1 objects
    _fields: list[data_models.Field] = []

    # Page 2 objects
    _imported_fields: list[data_models.Field] = []
    _detected_headers: list[str] = []
    _duplicated_input_headers: list[str] = []
    
    def get_persistence(self) -> FieldPersistence:
        return self.session[Persistence].get_field()

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self._fields = await self.get_persistence().get_all(self.session[data_models.AppUser])
        self._banner_factory = comps.BannerFactory("Field")
    
    async def _on_new_button_press(self) -> None:
        new_item = await comps.FieldDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"New Field",
            item=data_models.DialogItem(selection=data_models.Category.__name__),
        )

        result = await comps.FieldDialog.check_name_and_update_status(
            item=new_item,
            persistence=self.get_persistence(),
            banner_factory=self._banner_factory,
            parent=self,
        )
        if result:
            field = constants.FIELD_TYPE_DICT[new_item.selection]()
            field.set_owner(self.session[data_models.AppUser])
            field.header = new_item.name
            await self.get_persistence().insert_one(field)
            await self.on_populate()
            self._banner_factory.update(
                parent=self,
                status='created',
                name=new_item.name,
            )

    async def _on_delete_button_press(self, id: ObjectId, name: str) -> None:
        selected_value = await self.session.show_yes_no_dialog(
            title="Delete Field",
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

    async def _on_rename_button_press(self, id: ObjectId, header: str) -> None:
        new_item = await comps.SaveDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"Rename Field",
            item=data_models.DialogItem(header),
        )

        if new_item is None:
            return
        
        if new_item.name.strip() == "":
            self._banner_factory.update(
                parent=self,
                status='empty',
                name="",
            )
            return
        
        field = await self.get_persistence().find_one_by_header(self.session[data_models.AppUser], new_item.name)
        if field is not None:
            self._banner_factory.update(
                parent=self,
                status='already_exists',
                name=new_item.name,
            )
            return
        
        await self.get_persistence().update_header(id, new_item.name)
        await self.on_populate()
        self._banner_factory.update(
            parent=self,
            status='renamed',
            name=new_item.name,
        )

    async def _on_export_button_press(self) -> None:
        xlsx_data = XlsxGenerator.generate_field_def(
            fields=self._fields,
        )

        active_team = self.session[data_models.AppUser].active_team
        file_name = "Fields.xlsx" if active_team is None else f"Fields_{active_team}.xlsx"

        await self.session.save_file(
            file_contents=xlsx_data.getvalue(),
            file_name=file_name,
        )
    
    async def _on_import_button_press(self) -> None:
        new_item, df = await create_dialog_and_read_df(
            title="Import Field Definitions from File",
            sess=self.session,
            banner_factory=self._banner_factory,
            parent=self,
        )
        if new_item is None:
            return

        self._imported_fields, self._detected_headers = FieldsSerializer.deserialize_fields_from_df(df)
        counts = Counter(self._detected_headers)
        self._duplicated_input_headers = sorted([item for item, count in counts.items() if count > 1])

        # Save fields
        existing_field_headers = {field.header for field in self._fields}
        for field in self._imported_fields:
            if field.header in existing_field_headers:
                continue
            
            field.set_owner(self.session[data_models.AppUser])
            await self.get_persistence().insert_one(field)
        
        self.page = 2
        self._banner_factory.clear(parent=self)

    async def _on_delete_all_button_press(self) -> None:
        selected_value = await self.session.show_yes_no_dialog(
            title="Delete All Fields",
            text="Are you sure you want to delete all fields?",
        )
        if selected_value:
            await self.get_persistence().delete_all(self.session[data_models.AppUser])
            await self.on_populate()
            self._banner_factory.update(
                parent=self,
                status='delete_all',
            )
    
    async def _on_back_button_press(self) -> None:
        self.page = 1
        await self.on_populate()

    def build_page_1(self, title: str) -> rio.Component:
        return rio.Column(
            comps.TitleBar(
                page_name=title,
                buttons=[
                    comps.Button(
                        "Export",
                        on_press=self._on_export_button_press,
                    ),
                    comps.Button(
                        "Import",
                        on_press=self._on_import_button_press,
                    ),
                    comps.Button(
                        "Delete All",
                        on_press=self._on_delete_all_button_press,
                    ),
                ],
            ),
            comps.FilteredFieldTable(
                fields=self._fields,
                on_new_button_press=self._on_new_button_press,
                on_delete_button_press=self._on_delete_button_press,
                on_rename_button_press=self._on_rename_button_press,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )

    def build_import_summary_section(self, headers: set[str], title: str) -> list[rio.Component]:
        if len(headers) <= 0:
            return []
        
        content_fields = [rio.Text(text, font_size=1,margin_left=1,) for text in sorted(list(headers))]
        return [
            rio.Text(title, font_size=1.5, font_weight="bold"),
            rio.Column(
                *content_fields,
                align_x=0,
                margin_left=1,
            )
        ]
    
    def build_page_2(self, title: str) -> rio.Component:
        detected_headers = set(self._detected_headers)
        imported_headers = {field.header for field in self._imported_fields}
        existing_headers = {field.header for field in self._fields}
        error_headers = detected_headers - imported_headers
        ignored_headers = (imported_headers & existing_headers) | set(self._duplicated_input_headers)
        success_headers = imported_headers - existing_headers
        
        text = f"{len(self._detected_headers)} detected fields: {len(success_headers)} successfully imported, {len(error_headers)} contained errors, {len(ignored_headers)} duplicated and ignored."
        content = [
            rio.Text("Import Summary", font_size=1.5, font_weight="bold"),
            rio.Text(
                text,
                font_size=1,
                margin_left=1,
            )
        ]
        content.extend(self.build_import_summary_section(success_headers, "Successfully imported"))
        content.extend(self.build_import_summary_section(error_headers, "Errors"))
        content.extend(self.build_import_summary_section(ignored_headers, "Duplicated and ignored"))
        return rio.Column(
            comps.TitleBar(
                page_name=title,
                buttons=[
                    comps.Button(
                        "Back",
                        on_press=self._on_back_button_press,
                    ),
                ],
            ),
            rio.ScrollContainer(
                rio.Column(
                    *content,
                    spacing=0.5,
                    align_x=0,
                    align_y=0,
                ),
                margin=1,
                grow_x=True,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )

    def build(self) -> rio.Component:
        if self._fields is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )

        team = self.session[data_models.AppUser].active_team
        title = "Fields (under your personal space)"
        if team is not None:
            title = f"Fields (shared under team {team})"

        if self.page == 1:
            return self.build_page_1(title)
        else:
            return self.build_page_2(title)
    