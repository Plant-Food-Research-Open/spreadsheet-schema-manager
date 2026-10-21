from __future__ import annotations

import rio

from .. import components as comps
from .. import auth, data_models


@rio.page(
    name="Logout",
    url_segment="logout",
)
class LogoutPage(rio.Component):
    @rio.event.on_populate
    async def on_populate(self) -> None:
        try:
            self.session[data_models.AppUser]
            auth.logout()
            self.session.detach(data_models.AppUser)
        except KeyError:
            pass
        
        self.session.navigate_to("/login")

    def build(self) -> rio.Component:
        return rio.Spacer()
