from __future__ import annotations

import rio

from .. import components as comps
from .. import constants, auth
from ..release_notes import RELEASE_NOTES


@rio.page(
    name="Home",
    url_segment="",
    guard=auth.guard,
)
class HomePage(rio.Component):
    def build(self) -> rio.Component:
        latest_version = RELEASE_NOTES[0].version

        release_notes_column = rio.Column(
            comps.BoldText("Release Notes"),
            spacing=0.5,
            grow_y=True,
        )
        for note in RELEASE_NOTES:
            release_notes_column.add(
                rio.Column(
                    comps.BoldText(f"v{note.version} - {note.date}"),
                    rio.Column(
                        *[rio.Text(f"- {change}") for change in note.changes],
                        spacing=0.2,
                    ),
                    spacing=0.2,
                    margin_top=0.5,
                )
            )
        release_notes_column.add(rio.Spacer())

        return rio.Rectangle(
            content=rio.Column(
                rio.Card(
                    content=rio.Row(
                        rio.Text(
                            text=f"Welcome to Spreadsheet Schema Manager v{latest_version}!",
                            style='heading2',
                            font_weight='bold',
                        ),
                        align_x=0,
                    ),
                ),
                rio.Card(
                    content=rio.ScrollContainer(
                        release_notes_column,
                        grow_y=True,
                    ),
                    grow_y=True,
                ),
                rio.Card(
                    content=rio.Column(
                        comps.BoldText("Acknowledgements"),
                        rio.Text(
                            "Funded by the New Zealand Ministry of Business, Innovation and Employment Strategic Science Investment Fund (contract number C11X1702) as part of the Digital Horticulture Systems Ngā Pou Rangahau, a Growing Futures™ programme at The New Zealand Institute for Bioeconomy Science Limited (Bioeconomy Science Institute)",
                            overflow='wrap'),
                        rio.Text(
                            "Development team: Harris Lin, Peter Morrison-Whittle, Jane Tang, Chris Van Houtte, Marty Hickman, Jian Boey",
                            overflow='wrap'),
                        rio.Text(
                            "Staff who contributed to early testing: Maryam Alavi, Olivia Angelin-Bonnet, Charlotte Bridger, Carl Cerecke, Lindy Guo, Heather Jenkins, Hannah Lloyd, Stanley Mair, Nathanael Napier, Nicolette Niemann, LinLin Yang, Jingjing Zhang",
                            overflow='wrap'),
                        spacing=0.8,
                    ),
                ),
                spacing=1.5,
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
            fill=self.session.theme.neutral_color,
            grow_y=True,
        )

