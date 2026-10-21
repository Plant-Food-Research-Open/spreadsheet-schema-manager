from collections.abc import Callable

import rio
import functools

from .. import components as comps
from .. import constants, data_models


class StyledRectangle(rio.Component):
    """
    A custom component to display a rectangle with text and an icon.

    The option can be selected and deselected.


    ## Attributes:

    `name`: The name of the option.

    `is_selected`: A boolean indicating whether the option is selected.
    """

    name: str
    subname: str = ""
    is_selected: bool = False

    on_press: rio.EventHandler[[]] = None

    async def _on_press(self, _: rio.PointerEvent) -> None:
        await self.call_event_handler(self.on_press)

    def build(self) -> rio.Component:
        content = rio.Row(margin=0.5, spacing=0.5, min_height=1.2)
        content.add(
            rio.Text(
                self.name,
                selectable=False,
                style=rio.TextStyle(font_weight="bold", font_size=0.9, fill=constants.FILTER_TEXT_COLOR),
            ),
        )
        content.add(rio.Spacer())
        content.add(
            rio.Text(
                self.subname,
                selectable=False,
                style=rio.TextStyle(font_size=0.9, fill=constants.FILTER_TEXT_COLOR),
            ),
        )

        if self.is_selected:
            content.add(
                rio.Icon(
                    "material/check",
                    fill=self.session.theme.hud_color,
                    align_y=0.5,
                    min_width=1.2,
                    min_height=1.2,
                ),
            )
        else:
            content.add(rio.Row(min_width=1.2))

        return rio.PointerEventListener(
            rio.Rectangle(
                content=content,
                fill=rio.Color.TRANSPARENT,
                hover_fill=self.session.theme.background_color,
                corner_radius=self.session.theme.corner_radius_small,
                transition_time=0.1,
                cursor="pointer",
            ),
            on_press=self._on_press,
            # There's no ARIA "checked" state exposed by Rio for a custom
            # component like this, so a screen reader only gets the visible
            # name/subname text plus the checkmark icon's (unannounced)
            # presence; selection state isn't spoken.
            accessibility_role="button",
        )


class PopupRectangle(rio.Component):
    options: list[data_models.Option]

    on_change_option: rio.EventHandler[[data_models.Option]] = None

    def on_press(self, _: rio.PointerEvent) -> None:
        pass

    async def _on_change_option(self, option: data_models.Option) -> None:
        await self.call_event_handler(self.on_change_option, option)
        self.force_refresh()

    def build(self) -> rio.Component:
        content = rio.Column(margin=0.5, spacing=0.5, accessibility_role="menu")
        for option in self.options:
            content.add(
                StyledRectangle(
                    name=option.name,
                    subname=option.subname,
                    is_selected=option.is_selected,
                    on_press=functools.partial(self._on_change_option, option),
                ),
            )

        # Styling the popup
        return rio.PointerEventListener(
            rio.Rectangle(
                content=content,
                fill=self.session.theme.neutral_color,
                stroke_width=0.1,
                stroke_color=self.session.theme.neutral_color.brighter(0.2),
                corner_radius=self.session.theme.corner_radius_small,
                transition_time=0.1,
                align_x=0.5,
                min_width=7.5,
            ),
            on_press=self.on_press,
        )


class Filter(rio.Component):
    text: str
    icon: str
    popup_content: list[data_models.Option]
    text_fill: rio.Color = constants.FILTER_TEXT_COLOR
    is_open: bool = False

    on_change_option: rio.EventHandler[[data_models.Option]] = None

    async def _on_change_option(self, option: data_models.Option) -> None:
        await self.call_event_handler(self.on_change_option, option)

    def on_press(self, _: rio.PointerEvent) -> None:
        self.is_open = not self.is_open

    def build(self) -> rio.Component:
        return rio.Popup(
            # `accessibility_role` lives on `PointerEventListener` (the actual
            # interactive element); `Rectangle` has no `accessibility_label`
            # field, so the accessible name is derived from the visible
            # "Group"/"Type" text inside it.
            anchor=rio.PointerEventListener(
                rio.Rectangle(
                    content=rio.Row(
                        rio.Icon(
                            self.icon,
                            fill=constants.FILTER_TEXT_COLOR,
                            align_y=0.5,
                            min_width=1.2,
                            min_height=1.2,
                        ),
                        rio.Text(
                            self.text,
                            selectable=False,
                            style=rio.TextStyle(
                                fill=self.text_fill,
                                font_size=0.9,
                            ),
                        ),
                        rio.Spacer(),
                        rio.Icon(
                            "material/keyboard_arrow_down",
                            fill=constants.FILTER_TEXT_COLOR,
                            align_y=0.5,
                        ),
                        spacing=0.5,
                        margin_x=0.5,
                        margin_y=0.2,
                        align_y=0.5,
                    ),
                    fill=self.session.theme.background_color,
                    stroke_color=constants.FILTER_TEXT_COLOR,
                    hover_stroke_color=self.session.theme.primary_color,
                    stroke_width=0.1,
                    corner_radius=self.session.theme.corner_radius_small,
                ),
                on_press=self.on_press,
                accessibility_role="button",
            ),
            content=PopupRectangle(
                options=self.bind().popup_content,
                on_change_option=self._on_change_option,
            ),
            is_open=self.is_open,
            position="right",
        )


class FilterRow(rio.Component):
    group_options: list[data_models.Option]
    type_options: list[data_models.Option]

    on_change_status: rio.EventHandler[[data_models.Option]] = None
    on_new_button_press: Callable[[], None] | None = None
    add_button_label: str = "Add item"

    async def on_change_option(self, option: data_models.Option) -> None:
        await self.call_event_handler(self.on_change_status, option)

    def build(self) -> rio.Component:
        content = rio.Row(
            Filter(
                text="Group",
                icon="material/account_tree",
                popup_content=self.bind().group_options,
                on_change_option=self.on_change_option,
                min_width=10,
            ),
            Filter(
                text="Type",
                icon="material/category",
                popup_content=self.bind().type_options,
                on_change_option=self.on_change_option,
                min_width=10,
            ),
            rio.Spacer(),
            spacing=0.5,
            align_y=0.5,
            margin_x=1,
            margin_y=0.5,
        )

        if self.on_new_button_press:
            content.add(
                rio.IconButton(
                    "material/add",
                    min_size=constants.ICON_BUTTON_SIZE,
                    on_press=self.on_new_button_press,
                    margin_right=0.5,
                    accessibility_label=self.add_button_label,
                ),
            )

        return rio.Column(
            content,
            rio.Separator(
                color=self.session.theme.neutral_color,
                align_y=1,
            ),
            align_y=0,
        )


class AddNewRow(rio.Component):
    on_new_button_press: Callable[[], None] = lambda: None
    add_button_label: str = "Add item"

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Row(
                rio.Spacer(),
                rio.IconButton(
                    "material/add",
                    min_size=constants.ICON_BUTTON_SIZE,
                    on_press=self.on_new_button_press,
                    margin_right=0.5,
                    accessibility_label=self.add_button_label,
                ),
                spacing=0.5,
                align_y=0.5,
                margin_x=1,
                margin_y=0.5,
            ),
            rio.Separator(
                color=self.session.theme.neutral_color,
                align_y=1,
            ),
            align_y=0,
        )
