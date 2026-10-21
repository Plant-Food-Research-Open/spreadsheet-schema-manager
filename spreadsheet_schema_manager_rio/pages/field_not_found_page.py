import rio

from .. import auth


@rio.page(
    name="Field not found",
    url_segment="fieldnotfound",
    guard=auth.guard,
)
class FieldNotFoundPage(rio.Component):
    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text(
                text="Field not found! Please go back and update to latest Fields.",
                style="heading2",
            ),
            margin=1,
            align_y=0,
        )