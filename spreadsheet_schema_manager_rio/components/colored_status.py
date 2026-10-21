from __future__ import annotations

import rio

from ..data_models import DatasetStatus


class ColoredStatus(rio.Component):
    status: DatasetStatus

    def build(self) -> rio.Component:
        match self.status:
            case DatasetStatus.INVALID:
                color = rio.Color.from_hex("#FF6B6B")
                tip = "Error in spreadsheet format, click View for more details."
            case DatasetStatus.WARNING:
                color = rio.Color.from_hex("#FF7F27")
                tip = "Inconsistent formats found, click View for more details."
            case DatasetStatus.READY:
                color = rio.Color.from_hex("#3282F6")
                tip = "Ready to standardise, click Run to begin."
            case DatasetStatus.COMPLETE:
                color = rio.Color.from_hex("#4CAF50")
                tip = "Success! Click View or Download standardised data to see the result."
    
        return rio.Tooltip(
            anchor=rio.Rectangle(
                content=rio.Text(
                    self.status.name.capitalize(),
                    fill=color,
                    margin=0.2,
                    margin_x=0.5,
                ),
                fill=color.replace(opacity=0.2),
                stroke_color=color,
                stroke_width=0.1,
                corner_radius=self.session.theme.corner_radius_small,
                align_x=0,
                align_y=0.5,
            ),
            tip=tip,
        )
