import rio
import functools


class DropdownElement(rio.Component):
    """
    Single dropdown element component that displays an option and allows the
    user to select or deselect it.


    ## Attributes

    `option`: Option to be displayed in the dropdown.

    `is_selected`: Whether the option is selected.

    `icon_fill`: Fill color for the check icon when the option is selected.

    `font_style`: Text style for the option text.

    `on_press`: Event handler that is called when the option is pressed.
    """

    option: str
    is_selected: bool
    icon_fill: rio.Color

    font_style: rio.TextStyle = rio.TextStyle()
    on_press: rio.EventHandler[[]] = None

    async def _on_press(self, _: rio.PointerEvent) -> None:
        await self.call_event_handler(self.on_press)

    def _on_pointer_enter(self, _: rio.PointerEvent) -> None:
        # Change text style when entering
        self.font_style = rio.TextStyle(
            fill=self.session.theme.secondary_color,
            font_weight="bold",
        )
        # Change icon fill
        self.icon_fill = self.session.theme.secondary_color

    def _on_pointer_leave(self, _: rio.PointerEvent) -> None:
        # Change text style to default when leaving
        self.font_style = rio.TextStyle()
        # Change icon fill to the default text color and fix the type
        icon_fill_color = self.session.theme.text_style.fill
        if isinstance(icon_fill_color, rio.Color):
            self.icon_fill = icon_fill_color

    def build(self) -> rio.Component:
        # Create a row with the option text and a check icon if the option is
        # selected
        content_row = rio.Row(
            rio.Text(self.option, style=self.font_style),
            rio.Spacer(),
            margin_x=1,
            margin_y=0.25,
        )

        # Add a check icon if the option is selected
        if self.is_selected:
            content_row.add(
                rio.Icon("material/check", fill=self.icon_fill, min_height=1)
            )

        # Create a pointer event listener that changes the style of the option
        # when hovered and calls the on_press event handler when clicked
        return rio.PointerEventListener(
            rio.Rectangle(
                content=content_row,
                fill=rio.Color.TRANSPARENT,
                hover_fill=self.session.theme.primary_color.replace(opacity=0.2),
                cursor="pointer",
                transition_time=0.1,
                margin_x=0.2,
            ),
            on_pointer_enter=self._on_pointer_enter,
            on_pointer_leave=self._on_pointer_leave,
            on_press=self._on_press,
            accessibility_role="button",
        )


class DropdownLabel(rio.Component):
    """
    Dropdown label component that displays an option and allows the user to
    deselect it.


    ## Attributes

    `option`: Option to be displayed in the label.

    `on_press`: Event handler that is called when the label is pressed.
    """

    option: str
    on_press: rio.EventHandler[[]] = None

    async def _on_press(self) -> None:
        await self.call_event_handler(self.on_press)

    def format_option(self, option: str) -> str:
        """
        Format the option string to be displayed in the dropdown label.
        """
        if len(option) > 10:
            return f"{option[:8]}.."
        return option
        # parts = option.split()
        # if len(parts) == 2 and parts[0] == "Option":
        #     return f"O. {parts[1]}"
        # return option

    def build(self) -> rio.Component:
        return rio.Card(
            content=rio.Row(
                rio.Text(self.format_option(self.option)),
                rio.IconButton(
                    "material/close",
                    style="plain-text",
                    min_size=1.2,
                    on_press=self._on_press,
                    accessibility_label=f"Remove {self.option}",
                ),
                spacing=0.2,
                margin=0.2,
            ),
            color=self.session.theme.neutral_palette.background_variant,
            align_x=0.5,
            align_y=0.5,
        )


class DropdownHeader(rio.Component):
    """
    Dropdown header component that displays the selected options and allows the
    user to deselect options.


    ## Attributes

    `selected_options`: List of selected options.

    `label`: Label for the dropdown.

    `on_press_option`: Event handler that is called when a Dropdown Label is
    pressed.
    """

    selected_options: list[str]
    label: str
    on_press_option: rio.EventHandler[[str]] = None

    async def _on_press(self, selected_option: str) -> None:
        await self.call_event_handler(self.on_press_option, selected_option)
        self.force_refresh()

    def build(self) -> rio.Component:
        options_row = rio.Row(
            rio.Text(self.label),
            spacing=0.2,
            margin_x=0.2,
            # align_x=0,
        )
        # Populate the dropdown with elements and add labels for selected items.
        for selected_option in self.selected_options:
            options_row.add(
                DropdownLabel(
                    option=selected_option,
                    on_press=functools.partial(self._on_press, selected_option),
                )
            )

        # Add a spacer to align the dropdown icon to the right, ensuring it
        # remains positioned at the right edge of the dropdown header. This
        # guarantees consistent alignment regardless of the number of selected
        # options.
        options_row.add(
            rio.Spacer(),
        )

        # Add a dropdown icon
        options_row.add(
            rio.Icon(
                "material/keyboard_arrow_down",
            ),
        )

        return rio.Rectangle(
            content=options_row,
            fill=self.session.theme.neutral_color,
            corner_radius=self.session.theme.corner_radius_small,
            cursor="pointer",
            min_width=20,
            min_height=2,
        )


class CustomDropdown(rio.Component):
    """
    Custom dropdown component that allows the user to select multiple options
    from a list of options.


    ## Attributes

    `options`: All possible options and whether they are selected.

    `label`: Label for the dropdown.

    `_is_open`: Whether the popup is currently open.
    """

    options: dict[str, bool]
    label: str
    _is_open: bool = False

    def _on_press(self, _: rio.PointerEvent) -> None:
        self._is_open = not self._is_open

    def _on_option_press(self, option: str) -> None:
        self.options[option] = not self.options[option]
        self.force_refresh()

    def _get_selected_options(self) -> list[str]:
        return [option for option, is_selected in self.options.items() if is_selected]

    def build(self) -> rio.Component:
        # Create a column for the dropdown options
        dropdown_options = rio.Column(margin_y=0.2, accessibility_role="menu")

        # Change icon fill to the default text color and fix the type
        icon_fill_color = self.session.theme.text_style.fill
        if isinstance(icon_fill_color, rio.Color):
            icon_fill_typed = icon_fill_color

        # Populate the dropdown with elements and add labels for selected items.
        for option, is_selected in self.options.items():
            dropdown_options.add(
                DropdownElement(
                    option=option,
                    is_selected=is_selected,
                    on_press=functools.partial(self._on_option_press, option),
                    icon_fill=icon_fill_typed,
                )
            )

        # Create a popup that will be shown when the dropdown button is pressed
        # which has a similar appearance to a dropdown menu. Just combine the
        # header and the dropdown body.
        return rio.Popup(
            anchor=rio.PointerEventListener(
                DropdownHeader(
                    selected_options=self._get_selected_options(),
                    label=self.label,
                    on_press_option=self._on_option_press,
                ),
                on_press=self._on_press,
                accessibility_role="button",
            ),
            content=dropdown_options,
            position="dropdown",
            is_open=self._is_open,
            color="keep",
            # Make sure user can close the popup by clicking outside of it
            user_closable=True,
            corner_radius=self.session.theme.corner_radius_small,
        )