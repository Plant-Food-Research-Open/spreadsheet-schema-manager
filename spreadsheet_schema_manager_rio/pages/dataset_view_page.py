from __future__ import annotations
from abc import ABC, abstractmethod

import pandas as pd

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence
from ..s3_persistence import S3Persistence
from ..data_utils import data_clean_utils


@rio.page(
    name="Dataset",
    url_segment="datasets/{param_id}",
    guard=auth.guard,
)
class DatasetViewPage(rio.Component):
    param_id: str = ""
    content: rio.QueryParameter[str] = "raw"
    
    _dataset: data_models.Dataset | None = None
    _df: pd.DataFrame | None = None
    _validate_results: dict | None = None

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self._dataset = await self.session[Persistence].get_dataset().find_one_by_id(self.param_id)
        if self._dataset is None or (self.content != "raw" and self._dataset.status != data_models.DatasetStatus.COMPLETE):
            self.session.navigate_to("/")
            return
        
        if self.content == "raw":
            s3_obj = self._dataset.get_raw_s3_object()
        else:
            s3_obj = self._dataset.get_standardised_s3_object()
        file_obj = await self.session[S3Persistence].get_file(s3_obj)
        
        try:
            self._df = pd.read_csv(file_obj)
        except pd.errors.EmptyDataError:
            self._df = pd.DataFrame()
        
        self._validate_results = data_clean_utils.validate_format(self._df)

    def build(self) -> rio.Component:
        if self._validate_results is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )

        if self.content == "raw":
            prefix = "Raw"
        else:
            prefix = "Standardised"

        content = [
            rio.Text("Status", font_size=1.5, font_weight="bold"),
            rio.Text(
                self._validate_results["message"],
                font_size=1,
                margin_left=1,
            )
        ]

        if self._validate_results["errors"]:
            df = pd.DataFrame(self._validate_results["errors"].items(), columns=["Field", "Errors"])
            content.extend([
                rio.Text("Errors", font_size=1.5, font_weight="bold", margin_top=1),
                rio.Table(
                        data=df.fillna(""),
                        show_row_numbers=False,
                        align_x=0,
                        margin_left=1,
                        min_width=50,
                        accessibility_role="table",
                    ),
            ])

        if self._validate_results["warnings"]:
            df = pd.DataFrame(self._validate_results["warnings"].items(), columns=["Field", "Warnings"])
            content.extend([
                rio.Text("Warnings", font_size=1.5, font_weight="bold", margin_top=1),
                rio.Table(
                        data=df.fillna(""),
                        show_row_numbers=False,
                        align_x=0,
                        margin_left=1,
                        min_width=50,
                        accessibility_role="table",
                    ),
            ])

        content.extend([
            rio.Text("Field Type Summary (Totals)", font_size=1.5, font_weight="bold", margin_top=1),
            rio.Table(
                data=self._validate_results["profile"]["totals"].reset_index(names=["Totals"]).replace(0, ""),
                show_row_numbers=False,
                margin_left=1,
                accessibility_role="table",
            ),
            rio.Text("Field Type Summary (First Occurrence Row#)", font_size=1.5, font_weight="bold", margin_top=1),
            rio.Table(
                data=self._validate_results["profile"]["rows"].reset_index(names=["Row#"]),
                show_row_numbers=False,
                margin_left=1,
                accessibility_role="table",
            )
        ])

        df = pd.DataFrame(self._validate_results["types"].items(), columns=["Field", "Detected Type"])
        content.extend([
            rio.Text("Detected Types", font_size=1.5, font_weight="bold", margin_top=1),
            rio.Table(
                    data=df.fillna(""),
                    show_row_numbers=False,
                    align_x=0,
                    margin_left=1,
                    min_width=50,
                    accessibility_role="table",
                ),
        ])

        row_count = 100
        content.extend([
            rio.Text(f"Data (top {row_count} rows)", font_size=1.5, font_weight="bold", margin_top=1),
            rio.Table(
                data=self._df.head(row_count).fillna(""),
                show_row_numbers=False,
                margin_left=1,
                accessibility_role="table",
            ),
        ])

        return rio.Column(
            comps.TitleBar(
                page_name=f"{prefix} Dataset: {self._dataset.name}",
            ),
            rio.ScrollContainer(
                rio.Column(
                    *content,
                    spacing=0.5,
                    align_x=0,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_x=True,
                grow_y=True,
            ),
        )