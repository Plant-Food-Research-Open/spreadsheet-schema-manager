from __future__ import annotations
from abc import ABC, abstractmethod

from uniserde import ObjectId

import rio

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence


@rio.page(
    name="Field",
    url_segment="fields/{param_id}",
    guard=auth.guard,
)
class FieldPage(rio.Component):
    param_id: str = ""
    
    _banner_factory: comps.BannerFactory = comps.BannerFactory()
    _field: data_models.Field | None = None

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self._banner_factory = comps.BannerFactory("Field")
        self._field = await self.session[Persistence].get_field().find_one_by_id(self.param_id)
        if self._field is None:
            self.session.navigate_to("/fieldnotfound")
            return

    async def _on_save_button_press(self) -> None:
        is_valid, error_message = self._field.validate()
        if is_valid:
            await self.session[Persistence].get_field().upsert_one(self._field)
            self._banner_factory.update(
                parent=self,
                status='success',
                name=self._field.header,
            )
        else:
            self._banner_factory.update(
                parent=self,
                status='invalid',
                name=error_message,
            )
            return

        self.force_refresh()

    def build(self) -> rio.Component:
        if self._field is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )

        return rio.Column(
            comps.TitleBar(
                page_name=f"{self._field.__class__.__name__} Field: {self._field.header}",
                buttons=[
                    comps.Button(
                        "Save Field",
                        on_press=self._on_save_button_press,
                    ),
                ]
            ),
            comps.FieldInput(self._field),
            rio.Column(
                self._field.get_input_component(),
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )