import rio


class BoldText(rio.Component):
    text: str = ""

    def build(self) -> rio.Component:
        return rio.Text(
            self.text,
            style=rio.TextStyle(
                font_weight="bold",
            ),
        )