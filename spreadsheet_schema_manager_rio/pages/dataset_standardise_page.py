from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type
from io import BytesIO
from collections import Counter
import difflib
import functools

import pandas as pd

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..data_models import StandardisationSwitch
from ..persistence import Persistence
from ..s3_persistence import S3Persistence
from ..data_utils import data_clean_utils, data_standardise_utils
from ..data_utils.xlsx_generator import XlsxGenerator


@rio.page(
    name="DatasetStandardise",
    url_segment="standardise/{param_id}",
    guard=auth.guard,
)
class DatasetStandardisePage(rio.Component):
    param_id: str = ""
    page: int = 1
    
    # All page objects
    _banner_factory: comps.BannerFactory = comps.BannerFactory()
    _dataset: data_models.Dataset | None = None
    _df: pd.DataFrame | None = None
    _validate_results: dict | None = None
    _fields: list[data_models.Field] = []

    # Page 1 UI states
    _all_switch_selections: dict[str, StandardisationSwitch] = {}
    _all_field_selections: dict[str, data_models.Field] = {}
    _all_field_errors: dict[str, bool] = {}
    _all_type_selections: dict[str, Type[data_models.Field]] = {}

    # Page 2 UI states
    _all_text_switch_selections: dict[str, dict[str, StandardisationSwitch]] = {}
    _all_text_value_selections: dict[str, dict[str, data_models.Row]] = {}
    _all_new_text_values: dict[str, dict[str, str]] = {}
    _all_date_reliable: dict[str, bool] = {}
    _all_date_ambiguous: dict[str, bool] = {}
    _all_date_dayfirst_selections: dict[str, bool] = {}
    _finish_button_loading: bool = False
    
    # Any errors that prevent Finish
    _has_errors: bool = False

    def init_field_selections(self) -> None:
        fields_map = {field.header: field for field in self._fields}
        all_field_headers = list(fields_map.keys())
        for header in self._df.columns:
            close_match = difflib.get_close_matches(header, all_field_headers, n=1)
            if close_match:
                self._all_switch_selections[header] = StandardisationSwitch.EXISTING
                self._all_field_selections[header] = fields_map[close_match[0]]
            else:
                self._all_switch_selections[header] = StandardisationSwitch.NEW
                if self._fields:
                    self._all_field_selections[header] = self._fields[0]
            
            self._all_field_errors[header] = False
            self._all_type_selections[header] = constants.FIELD_TYPE_DICT[self._validate_results["types"][header].split()[0]]
    
    def init_text_selections(self, header: str, uniques: list[str]) -> None:
        text_switch_selections = {}
        text_value_selections = {}
        values_map = {row.header: row for row in self._all_field_selections[header].values}
        all_values = list(values_map.keys())
        for unique in uniques:
            close_match = difflib.get_close_matches(unique, all_values, n=1)
            if close_match:
                text_switch_selections[unique] = StandardisationSwitch.EXISTING
                text_value_selections[unique] = values_map[close_match[0]]
            else:
                text_switch_selections[unique] = StandardisationSwitch.NEW
                text_value_selections[unique] = values_map[all_values[0]] if all_values else None

        self._all_text_switch_selections[header] = text_switch_selections
        self._all_text_value_selections[header] = text_value_selections

    def has_selected_category_type(self, header: str) -> bool:
        if self._all_switch_selections[header] == StandardisationSwitch.EXISTING:
            return isinstance(self._all_field_selections[header], data_models.Category)
        else:
            return self._all_type_selections[header] == data_models.Category

    def has_selected_date_type(self, header: str) -> bool:
        if self._all_switch_selections[header] == StandardisationSwitch.EXISTING:
            return isinstance(self._all_field_selections[header], data_models.Date)
        else:
            return self._all_type_selections[header] == data_models.Date

    def date_order_switcherbar_on_change(self, header: str, event: rio.SwitcherBarChangeEvent) -> None:
        self._all_date_dayfirst_selections[header] = event.value

    def get_df_unique_str(self, header: str) -> list[str]:
        return sorted(self._df[header].dropna().astype(str).unique())

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self._banner_factory = comps.BannerFactory("")
        self._dataset = await self.session[Persistence].get_dataset().find_one_by_id(self.param_id)
        self._fields = await self.session[Persistence].get_field().get_all(self.session[data_models.AppUser])
        if self._dataset is None:
            self.session.navigate_to("/")
            return
        
        s3_obj = self._dataset.get_raw_s3_object()
        file_obj = await self.session[S3Persistence].get_file(s3_obj)
        
        try:
            self._df = pd.read_csv(file_obj)
        except pd.errors.EmptyDataError:
            self._df = pd.DataFrame()
        
        self._validate_results = data_clean_utils.validate_format(self._df)
        self._df = self._df.fillna("")
        self.init_field_selections()
        
    async def _on_next_button_press(self) -> None:
        self._has_errors = False
        self._all_field_errors = {header: False for header in self._df.columns}
        
        # Check for duplicated mapped_fields
        mapped_fields = [self._all_field_selections[header].header for header in self._df.columns if self._all_switch_selections[header] == StandardisationSwitch.EXISTING]
        duplicated_mapped_fields = {item for item, count in Counter(mapped_fields).items() if count > 1}
        if duplicated_mapped_fields:
            self._has_errors = True
            for header in self._df.columns:
                if self._all_switch_selections[header] == StandardisationSwitch.EXISTING and self._all_field_selections[header].header in duplicated_mapped_fields:
                    self._all_field_errors[header] = True
            
            self._banner_factory.update(
                parent=self,
                status='duplicate_map',
                name=list(duplicated_mapped_fields)[0],
            )
            return
        
        # Check for Category Fields with empty values
        empty_category_fields = []
        for header in self._df.columns:
            if self._all_switch_selections[header] == StandardisationSwitch.EXISTING and isinstance(self._all_field_selections[header], data_models.Category):
                if not self._all_field_selections[header].values:
                    self._all_field_errors[header] = True
                    empty_category_fields.append(self._all_field_selections[header].header)
        if empty_category_fields:
            self._has_errors = True
            self._banner_factory.update(
                parent=self,
                status='empty_category_field',
                name=empty_category_fields[0],
            )
            return

        # Proceed to Page 2
        
        # Check for mapping limit and reset Page 2 selections
        for header in self._df.columns:
            if self.has_selected_category_type(header):
                uniques = self.get_df_unique_str(header)
                if len(uniques) > constants.MAX_CATEGORY_VALUES:
                    self._has_errors = True
                else:
                    if self._all_switch_selections[header] == StandardisationSwitch.EXISTING:
                        self.init_text_selections(header, uniques)
                    else:
                        self._all_text_switch_selections[header] = {value: StandardisationSwitch.NEW for value in uniques}
                    
                    self._all_new_text_values[header] = {unique: unique for unique in uniques}
            else:
                self._all_text_switch_selections[header] = {}
                self._all_text_value_selections[header] = {}
                self._all_new_text_values[header] = {}

            if self.has_selected_date_type(header):
                is_reliable, is_ambiguous, dayfirst = data_standardise_utils.check_date_format_reliability(self._df[header])
                self._all_date_reliable[header] = is_reliable
                self._all_date_ambiguous[header] = is_ambiguous
                if is_reliable:
                    # Day-first is this app's default (NZ/AU convention) when
                    # ambiguous - dayfirst is None only in that case, since a
                    # reliable, unambiguous column always has a real answer.
                    self._all_date_dayfirst_selections[header] = dayfirst if dayfirst is not None else True
                else:
                    self._all_date_dayfirst_selections.pop(header, None)
                    self._has_errors = True
            else:
                self._all_date_reliable.pop(header, None)
                self._all_date_ambiguous.pop(header, None)
                self._all_date_dayfirst_selections.pop(header, None)

        self.page = 2
        self._banner_factory.clear(parent=self)
    
    async def _on_back_button_press(self) -> None:
        self.page = 1
        self.force_refresh()
    
    async def _on_finish_button_press(self) -> None:
        self._finish_button_loading = True

        user = self.session[data_models.AppUser]

        df_std, fields, updated_fields, standardisation_log_df = data_standardise_utils.standardise_fields(
            self._fields,
            self._df,
            user.date_format,
            self._all_switch_selections,
            self._all_field_selections,
            self._all_type_selections,
            self._all_text_switch_selections,
            self._all_text_value_selections,
            self._all_new_text_values,
            self._all_date_dayfirst_selections,
        )

        # Update Fields
        for field in updated_fields:
            field.set_owner(self.session[data_models.AppUser])
            await self.session[Persistence].get_field().upsert_one(field)
        
        # Save standardised dataset to S3
        out_file_obj = BytesIO()
        df_std.to_csv(out_file_obj, index=False)
        out_file_obj.seek(0)
        await self.session[S3Persistence].save_file(out_file_obj, self._dataset.get_standardised_s3_object())
        out_file_obj.close()

        # Create Workbook with fields
        workbook = data_models.Workbook.new_empty(user, fields)
        workbook.name = self._dataset.name
        workbook.select_all_fields()

        # Save workbook to S3, with data
        xlsx_data = XlsxGenerator.generate_workbook(
            workbook=workbook,
            date_format=user.date_format,
            df=df_std,
            include_constant_category=True,
            standardisation_log_df=standardisation_log_df,
        )
        xlsx_data.seek(0)
        await self.session[S3Persistence].save_file(xlsx_data, self._dataset.get_standardised_xlsx_s3_object())
        xlsx_data.close()

        # Update dataset status
        self._dataset.status = data_models.DatasetStatus.COMPLETE
        await self.session[Persistence].get_dataset().upsert_one(self._dataset)

        self._finish_button_loading = False

        # Show success dialog
        await comps.TextDialog.create_dialog_item_editor(
            sess=self.session,
            title=f"Dataset {self._dataset.name} successfully standardised, now redirecting to Datasets page to view and download them...",
        )

        self.session.navigate_to("/datasets")

    def build_page_1(self) -> rio.Component:
        return rio.Column(
            comps.TitleBar(
                page_name=f"Standardising Dataset: {self._dataset.name}",
                buttons=[
                    comps.Button(
                        "Next",
                        on_press=self._on_next_button_press,
                    ),
                ]
            ),
            rio.ScrollContainer(
                rio.Column(
                    comps.StandardiseFieldTable(
                        rows=self._df.columns.tolist(),
                        fields=self._fields,
                        all_switch_selections=self._all_switch_selections,
                        all_field_selections=self._all_field_selections,
                        all_field_errors=self._all_field_errors,
                        all_type_selections=self._all_type_selections,
                        grow_y=True,         
                    ),
                    spacing=0.5,
                    align_x=0,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )

    def build_page_2(self) -> rio.Component:
        content = []
        for header in self._df.columns:
            if self._all_switch_selections[header] == StandardisationSwitch.EXISTING:
                text = f"Mapping {header} to {self._all_field_selections[header].header} ({self._all_field_selections[header].__class__.__name__})"
            else:
                text = f"Mapping {header} to a new {self._all_type_selections[header].__name__} Field"
            content.append(
                rio.Text(text, font_size=1.5, margin_top=1)
            )

            if self.has_selected_category_type(header):
                uniques = self.get_df_unique_str(header)
                if len(uniques) == 0:
                    content.append(
                        rio.Text(
                            f"Warning: {header} has no values available to map.",
                            fill=self.session.theme.warning_color,
                            margin=constants.PAGE_MARGIN_X,
                        )
                    )
                elif len(uniques) > constants.MAX_CATEGORY_VALUES:
                    content.append(
                        rio.Text(
                            f"Error: {header} has {len(uniques)} unique values, which exceeds the mapping limit of {constants.MAX_CATEGORY_VALUES}.",
                            fill=self.session.theme.danger_color,
                            margin=constants.PAGE_MARGIN_X,
                        )
                    )
                elif self._all_switch_selections[header] == StandardisationSwitch.EXISTING:
                    content.append(
                        comps.StandardiseValueTable(
                            rows=uniques,
                            field_values=self._all_field_selections[header].values,
                            text_switch_selections=self._all_text_switch_selections.get(header),
                            text_value_selections=self._all_text_value_selections.get(header),
                            new_text_values=self._all_new_text_values.get(header),
                            margin=constants.PAGE_MARGIN_X,
                            grow_y=True,
                        )
                    )
                else:
                    content.append(
                        comps.StandardiseValueTable(
                            rows=uniques,
                            field_values=[],
                            text_switch_selections=self._all_text_switch_selections.get(header),
                            text_value_selections={},
                            new_text_values=self._all_new_text_values.get(header),
                            margin=constants.PAGE_MARGIN_X,
                            grow_y=True,
                        )
                    )
            elif self.has_selected_date_type(header):
                if not self._all_date_reliable.get(header, False):
                    content.append(
                        rio.Text(
                            f"Error: {header} does not have a consistent, reliable date format. Please fix, or map to a Text field instead.",
                            fill=self.session.theme.danger_color,
                            margin=constants.PAGE_MARGIN_X,
                        )
                    )
                elif self._all_date_ambiguous.get(header):
                    content.append(
                        rio.Row(
                            rio.Text("Ambiguous date format, please specify:"),
                            rio.SwitcherBar(
                                rio.SwitcherBarItem(True, "Day first"),
                                rio.SwitcherBarItem(False, "Month first"),
                                selected_value=self._all_date_dayfirst_selections.get(header, True),
                                on_change=functools.partial(self.date_order_switcherbar_on_change, header),
                            ),
                            align_x=0,
                            spacing=0.5,
                            margin=constants.PAGE_MARGIN_X,
                        )
                    )
                elif header in self._dataset.native_date_columns:
                    content.append(
                        rio.Text(
                            "Excel native date format detected - no ambiguity to resolve.",
                            margin=constants.PAGE_MARGIN_X,
                        )
                    )
                else:
                    detected_format = data_standardise_utils.resolve_date_format(
                        self._df[header], self._all_date_dayfirst_selections.get(header, True)
                    )
                    content.append(
                        rio.Text(
                            f"Detected date format: {detected_format}",
                            margin=constants.PAGE_MARGIN_X,
                        )
                    )

            content.append(
                rio.Separator()
            )

        return rio.Column(
            comps.TitleBar(
                page_name=f"Standardising Dataset: {self._dataset.name}",
                buttons=[
                    comps.Button(
                        "Back",
                        on_press=self._on_back_button_press,
                    ),
                    comps.Button(
                        "Finish",
                        on_press=self._on_finish_button_press,
                        is_sensitive=not self._has_errors,
                        is_loading=self._finish_button_loading,
                    ),
                ]
            ),
            rio.ScrollContainer(
                rio.Column(
                    *content,
                    spacing=0.5,
                    align_x=0,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )

    def build(self) -> rio.Component:
        if self._validate_results is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )

        if self.page == 1:
            return self.build_page_1()
        else:
            return self.build_page_2()
    