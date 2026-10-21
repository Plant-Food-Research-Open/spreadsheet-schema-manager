from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field

import rio

from .. import components as comps
from .. import constants, data_models


class TitleBar(rio.Component):
    page_name: str = ""
    buttons: list[comps.Button | rio.Link] = []
    buttons_rhs: list[comps.Button | rio.Link] = []
    
    def build(self) -> rio.Component:
        bar = rio.Column(
            rio.Rectangle(
                # Row layout to arrange items horizontally
                content=rio.Row(
                    rio.Text(
                        self.page_name,
                        font_size=2,
                        font_weight="bold",
                        accessibility_role="heading",
                    ),
                    rio.Spacer(),  # Spacer to push items to the right
                    spacing=1,
                    margin_right=1+self.session.scroll_bar_size,
                    margin_left=constants.PAGE_MARGIN_X,
                ),
                align_y=0,
                min_height=5,
            )
        )

        if len(self.buttons_rhs) == 0:
            self.buttons_rhs.append(rio.Spacer())
        else:
            self.buttons.append(rio.Spacer())

        if len(self.buttons) > 0:
            bar.add(
                rio.Rectangle(
                    # Row layout to arrange items horizontally
                    content=rio.Row(
                        *self.buttons,
                        *self.buttons_rhs,
                        spacing=1,
                        margin_right=1+self.session.scroll_bar_size,
                        accessibility_role="toolbar",
                    ),
                    align_y=0,
                    margin_bottom=1,
                    margin_left=constants.PAGE_MARGIN_X,
                )
            )

        bar.add(
            rio.Rectangle(
                fill=self.session.theme.neutral_color.darker(0.1),
                min_height=0.3,
                align_y=0,
            ),
        )
        return bar

