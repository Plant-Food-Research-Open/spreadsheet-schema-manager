import rio

from .. import constants, data_models


class ReorderableFieldList(rio.Component):
    fields: list[data_models.Field] = []

    def on_swap_button_press(self, index: int, direction: int):
        target = index + direction
        self.fields[index], self.fields[target] = self.fields[target], self.fields[index]
        self.force_refresh()

    def build(self) -> rio.Component:
        list_column = rio.Column(
            spacing=0.3,
            margin=0.2,
            align_x=0,
            align_y=0,
        )
        for i, field in enumerate(self.fields):
            is_first = (i == 0)
            is_last = (i == len(self.fields) - 1)
            item_card = rio.Card(
                content=rio.Row(
                    rio.Text(field.header),
                    rio.Spacer(min_width=2),
                    rio.IconButton(
                        icon="material/arrow_upward",
                        min_size=2.2,
                        is_sensitive=not is_first,
                        on_press=lambda i=i: self.on_swap_button_press(i, -1),
                        accessibility_label=f"Move {field.header} up",
                    ),
                    rio.IconButton(
                        icon="material/arrow_downward",
                        min_size=2.2,
                        is_sensitive=not is_last,
                        on_press=lambda i=i: self.on_swap_button_press(i, 1),
                        accessibility_label=f"Move {field.header} down",
                    ),
                    spacing=0.4,
                    margin=0.2,
                    margin_left=0.5,
                ),
                corner_radius=0,
            )
            list_column.add(item_card)

        return list_column