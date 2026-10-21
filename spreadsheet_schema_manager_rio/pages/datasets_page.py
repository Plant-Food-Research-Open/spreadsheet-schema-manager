from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type

import os
from io import BytesIO
import pandas as pd
from bson import ObjectId

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence, DatasetPersistence, FieldPersistence
from ..s3_persistence import S3Persistence
from ..data_utils.data_clean_utils import extract_fixed_table, validate_format
from ..data_utils.df_reader import create_dialog_and_read_df


@rio.page(
    name="Datasets",
    url_segment="datasets",
    guard=auth.guard,
)
class DatasetsPage(rio.Component):
    datasets: list[data_models.Dataset] = []
    
    _dataset_map: dict[ObjectId, data_models.Dataset] = {}
    _banner_factory: comps.BannerFactory = comps.BannerFactory()

    def get_title(self) -> str:
        team = self.session[data_models.AppUser].active_team
        if team is None:
            return "Datasets uploaded by me (under your personal space)"
        else:
            return f"Datasets uploaded by me (under team {team})"

    def get_persistence(self) -> DatasetPersistence:
        return self.session[Persistence].get_dataset()

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self.datasets = await self.get_persistence().get_all(self.session[data_models.AppUser])
        self._dataset_map = {dataset.id: dataset for dataset in self.datasets}
        self._banner_factory = comps.BannerFactory(data_models.Dataset.__name__)

    async def _on_new_button_press(self) -> None:
        new_item, df = await create_dialog_and_read_df(
            title=f"Upload {data_models.Dataset.__name__}",
            sess=self.session,
            banner_factory=self._banner_factory,
            parent=self,
        )
        if new_item is None:
            return
        
        result = await comps.FileDialog.check_name_and_update_status(
            item=new_item,
            persistence=self.get_persistence(),
            banner_factory=self._banner_factory,
            parent=self
        )
        if result:
            out_file_obj = BytesIO()
            df = extract_fixed_table(df)
            # pd.read_csv never produces datetime64 columns on its own, so this
            # only ever picks up columns that were genuine Excel date cells -
            # not, say, a Text column in the sheet that merely looks like a date.
            native_date_columns = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
            validate_results = validate_format(df)
            df.fillna("").to_csv(out_file_obj, index=False, float_format="%g")

            dataset = data_models.Dataset.new_empty(self.session[data_models.AppUser])
            dataset.name = new_item.name
            dataset.status = validate_results["status"]
            dataset.native_date_columns = native_date_columns
            new_id = await self.get_persistence().insert_one(dataset)
            dataset.id = new_id
            out_file_obj.seek(0)
            await self.session[S3Persistence].save_file(out_file_obj, dataset.get_raw_s3_object())
            out_file_obj.close()
            await self.on_populate()
            self._banner_factory.update(
                parent=self,
                status='uploaded',
                name=new_item.name,
            )

    async def _on_download_raw_button_press(self, id: ObjectId) -> None:
        dataset = self._dataset_map[id]
        file_obj = await self.session[S3Persistence].get_file(dataset.get_raw_s3_object())
        await self.session.save_file(
            file_contents=file_obj.read(),
            file_name=f"{dataset.name}.csv",
        )
    
    async def _on_download_standardised_button_press(self, id: ObjectId) -> None:
        dataset = self._dataset_map[id]
        file_obj = await self.session[S3Persistence].get_file(dataset.get_standardised_xlsx_s3_object())
        await self.session.save_file(
            file_contents=file_obj.read(),
            file_name=f"{dataset.name}.std.xlsx",
        )
    
    async def _on_delete_button_press(self, id: ObjectId, name: str) -> None:
        selected_value = await self.session.show_yes_no_dialog(
            title=f"Delete {data_models.Dataset.__name__}",
            text=f"Are you sure you want to delete {name}?",
        )
        if selected_value:
            await self.get_persistence().delete_one(id)
            dataset = self._dataset_map[id]
            await self.session[S3Persistence].delete_file(dataset.get_raw_s3_object())
            await self.session[S3Persistence].delete_file(dataset.get_standardised_s3_object())
            await self.session[S3Persistence].delete_file(dataset.get_standardised_xlsx_s3_object())            
            await self.on_populate()
            self._banner_factory.update(
                parent=self,
                status='deleted',
                name=name,
            )

    async def _on_rename_button_press(self, id: ObjectId, name: str) -> None:
        new_item = await comps.SaveDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"Rename {data_models.Dataset.__name__}",
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
        
    def build(self) -> rio.Component:
        if self.datasets is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )
        
        return rio.Column(
            comps.TitleBar(self.get_title()),
            comps.FilteredDatasetTable(
                datasets=self.datasets,
                on_new_button_press=self._on_new_button_press,
                on_download_raw_button_press=self._on_download_raw_button_press,
                on_download_standardised_button_press=self._on_download_standardised_button_press,
                on_delete_button_press=self._on_delete_button_press,
                on_rename_button_press=self._on_rename_button_press,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )
