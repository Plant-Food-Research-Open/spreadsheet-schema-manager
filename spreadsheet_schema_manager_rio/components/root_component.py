from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field

import rio

from .. import components as comps
from .. import data_models


class RootComponent(rio.Component):
    """
    This page will be used as the root component for the app. This means, that
    it will always be visible, regardless of which page is currently active.

    This makes it the perfect place to put components that should be visible on
    all pages, such as a navbar or a footer.

    Additionally, the root page will contain a `rio.PageView`. Page views don't
    have any appearance on their own, but they are used to display the content
    of the currently active page. Thus, we'll always see the Sidebar with the
    content of the current page next to it.
    """

    def desktop_build(self) -> rio.Component:
        return rio.Row(
            # The Sidebar contains a `rio.Overlay`, so it will always be on top
            # of all other components.
            comps.NavBar(),
            rio.Separator(
                min_width=0.3,
                color=self.session.theme.neutral_color.darker(0.1),
            ),
            # The page view will display the content of the current page.
            rio.Column(
                rio.PageView(
                    # Make sure the page view takes up all available space.
                    grow_y=True,
                ),
                # Make sure the page view takes up all available space.
                grow_x=True,
                accessibility_role="main",
            ),
        )

    def build(self) -> rio.Component:
        return self.desktop_build()
