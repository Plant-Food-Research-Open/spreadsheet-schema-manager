from __future__ import annotations

import rio

from bson import ObjectId

from .. import components as comps
from .. import constants, data_models, auth
from ..persistence import Persistence


@rio.page(
    name="Settings",
    url_segment="settings",
    guard=auth.guard,
)
class SettingsPage(rio.Component):
    selected_team: data_models.AppTeam | None = None
    _banner_factory: comps.BannerFactory = comps.BannerFactory()

    @rio.event.on_populate
    async def on_populate(self) -> None:
        self.selected_team = self.session[data_models.AppUser].active_team
        self._banner_factory = comps.BannerFactory("Settings")
    
    async def _on_save_button_press(self) -> None:
        user = self.session[data_models.AppUser]
        user.active_team = self.selected_team
        await self.session[Persistence].upsert_user(user)
        self._banner_factory.update(
            parent=self,
            status='success',
            name="",
        )
    
    def constant_category_checkbox_on_change(self, event: rio.CheckboxChangeEvent) -> None:
        user = self.session[data_models.AppUser]
        user.include_constant_category = event.is_on

    def date_format_dropdown_on_change(self, event: rio.DropdownChangeEvent) -> None:
        user = self.session[data_models.AppUser]
        user.date_format = event.value
    
    def build(self) -> rio.Component:
        user = self.session[data_models.AppUser]
        team_list = [None]
        team_list.extend(user.joined_teams)

        return rio.Column(
            comps.TitleBar(
                page_name="Settings",
                buttons=[
                    comps.Button(
                        "Save Settings",
                        on_press=self._on_save_button_press,
                    ),
                ]
            ),
            rio.Column(
                rio.Row(
                    comps.BoldText("Logged in as:"),
                    comps.BoldText(user.name),
                    align_x=0,
                    spacing=0.5,
                ),
                rio.Row(
                    rio.Text("Current active team:"),
                    rio.Dropdown(
                        options=team_list,
                        selected_value=self.bind().selected_team,
                    ),
                    align_x=0,
                    spacing=0.5,
                ),
                rio.Row(
                    rio.Text("Preferred date format:"),
                    rio.Dropdown(
                        options=constants.DATE_FORMATS,
                        selected_value=user.date_format,
                        on_change=self.date_format_dropdown_on_change,
                    ),
                    align_x=0,
                    spacing=0.5,
                ),
                rio.Row(
                    rio.Checkbox(
                        user.include_constant_category,
                        on_change=self.constant_category_checkbox_on_change,
                    ),
                    rio.Text("Include constant Category fields in the raw data sheet of a downloaded Workbook."),
                    align_x=0,
                    spacing=0.5,
                ),
                margin=constants.PAGE_MARGIN_X,
                align_y=0,
                spacing=1.0,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )

