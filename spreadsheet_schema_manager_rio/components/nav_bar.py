from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field

import rio

from .. import components as comps
from .. import constants, data_models


class NavBar(rio.Component):
    """
    Represents the sidebar component of the application.

    The sidebar includes:
    - A Rio logo at the top.
    - A list of major sections dynamically highlighted based on the active URL
    segment.
    - Spacer to separate content for better layout alignment.
    """

    _is_open: bool = False

    # Make sure the navbar will be rebuilt when the app navigates to a different
    # page. While Rio automatically detects state changes and rebuilds
    # components as needed, navigating to other pages is not considered a state
    # change, since it's not stored in the component.
    #
    # Instead, we can use Rio's `on_page_change` event to trigger a rebuild of
    # the navbar when the page changes.
    @rio.event.on_page_change
    def on_page_change(self) -> None:
        """
        Trigger a rebuild of the navbar when the page changes.
        """
        # Rio comes with a function specifically for this. Whenever Rio is
        # unable to detect a change automatically, use this function to force a
        # refresh.
        self.force_refresh()

    def _on_switcherbar_value_change(
        self, event: rio.SwitcherBarChangeEvent
    ) -> None:
        """
        Handles changes to the SwitcherBar value.

        Navigates to the corresponding page and closes the mobile menu.
        """
        # Navigate to the target page
        self.session.navigate_to(f"/{event.value}")
        # Close the mobile menu
        self._is_open = False

    def desktop_build(self) -> rio.Component:
        """
        Build the desktop layout.
        """
        # Retrieve the current active page's URL segment
        active_url_segment = self.session.active_page_url.path

        # Create a column to hold the main sections
        content = rio.Column(spacing=1)

        # Add each major section to the sidebar, highlighting the active section
        for section in constants.MAIN_SECTIONS:
            content.add(
                # Link the section to the corresponding page
                rio.Link(
                    comps.MajorSection(
                        main_section=section,
                        is_active=section.target_url == active_url_segment,
                    ),
                    section.target_url,
                ),
            )

        content.add(rio.Spacer())

        for section in constants.FOOTER_SECTIONS:
            content.add(
                # Link the section to the corresponding page
                rio.Link(
                    comps.MajorSection(
                        main_section=section,
                        is_active=section.target_url == active_url_segment,
                    ),
                    section.target_url,
                ),
            )

        return rio.Rectangle(
            content=rio.Column(
                content,
                margin_x=1,
                margin_y=1,
                align_x=0,
                min_width=10,
            ),
            fill=self.session.theme.neutral_color,
            accessibility_role="navigation",
        )

    def build(self) -> rio.Component:
        return self.desktop_build()

