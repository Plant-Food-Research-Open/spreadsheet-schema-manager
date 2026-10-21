from __future__ import annotations
from abc import ABC, abstractmethod

from uniserde import ObjectId

import rio

from .. import components as comps
from .. import constants, data_models


class FieldInputComponent(rio.Component):
    field: data_models.Field

    def build(self) -> rio.Component:
        return rio.Column()


class NumberInputComponent(FieldInputComponent):
    pass


class TextInputComponent(FieldInputComponent):
    pass


class DateInputComponent(FieldInputComponent):
    pass


class CategoryInputComponent(FieldInputComponent):
    def build(self) -> rio.Component:
        return comps.FilteredTextInputTable(
            field=self.field,
        )


class MeasurementInputComponent(FieldInputComponent):
    def build(self) -> rio.Component:
        def on_trait_value_change(event: rio.TextInputChangeEvent):
            self.field.trait = event.text

        def on_unit_value_change(event: rio.TextInputChangeEvent):
            self.field.unit = event.text

        def on_method_value_change(event: rio.TextInputChangeEvent):
            self.field.method = event.text

        return rio.Column(
            rio.Row(
                rio.TextInput(
                    text=self.field.trait,
                    on_change=on_trait_value_change,
                    label="Trait",
                    min_width=40,
                ),
                rio.Spacer(),
            ),
            rio.Row(
                rio.TextInput(
                    text=self.field.unit,
                    on_change=on_unit_value_change,
                    label="Unit",
                    min_width=20,
                ),
                rio.Spacer(),
            ),
            rio.TextInput(
                text=self.field.method,
                on_change=on_method_value_change,
                label="Method",
            ),
            rio.Column(
                comps.FilteredParamInputTable(
                    field=self.field,
                ),
                grow_y=True,
            ),
            spacing=0.5,
        )



class FieldInput(rio.Component):
    field: data_models.Field

    def build(self) -> rio.Component:
        def on_group_value_change(event: rio.TextInputChangeEvent):
            self.field.group = event.text

        def on_desc_value_change(event: rio.TextInputChangeEvent):
            self.field.desc = event.text

        def on_ref_value_change(event: rio.TextInputChangeEvent):
            self.field.ref = event.text
        
        return rio.Column(
            rio.TextInput(
                text=self.field.group,
                on_change=on_group_value_change,
                label="Group",
                align_x=0,
                min_width=25,
                margin_bottom=0.5,
            ),
            rio.TextInput(
                text=self.field.desc,
                on_change=on_desc_value_change,
                label="Description",
            ),
            rio.TextInput(
                text=self.field.ref,
                on_change=on_ref_value_change,
                label="Reference URL",
            ),            
            align_y=0,
            spacing=0.5,
            margin=constants.PAGE_MARGIN_X,
        )
