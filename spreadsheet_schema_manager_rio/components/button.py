import dataclasses
import typing as t

import rio


class Button(rio.Component):
    """A `rio.Button` that always exposes an accessible `button` role.

    Plain `rio.Button` instances render with no ARIA role at all in this
    version of rio-ui: `accessibility_label` alone sets an `aria-label`, but
    without a `role="button"` to go with it, browsers won't expose a
    computed accessible name, so screen readers and role-based automation
    can't find the button. Use this everywhere in place of `rio.Button`.
    """

    content: str | rio.Component = ""
    _: dataclasses.KW_ONLY
    icon: str | None = None
    shape: t.Literal["pill", "rounded", "rectangle"] = "pill"
    style: t.Literal[
        "major", "minor", "colored-text", "plain-text", "plain"
    ] = "major"
    color: rio.ColorSet = "keep"
    is_sensitive: bool = True
    is_loading: bool = False
    on_press: rio.EventHandler[[]] = None
    accessibility_label: str | None = None

    def build(self) -> rio.Component:
        return rio.Button(
            self.content,
            icon=self.icon,
            shape=self.shape,
            style=self.style,
            color=self.color,
            is_sensitive=self.is_sensitive,
            is_loading=self.is_loading,
            on_press=self.on_press,
            accessibility_label=self.accessibility_label,
            accessibility_role="button",
        )
