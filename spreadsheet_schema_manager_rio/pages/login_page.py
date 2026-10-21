from __future__ import annotations

import rio

from .. import components as comps
from .. import auth, data_models
from ..persistence import Persistence


def guard(event: rio.GuardEvent) -> str | None:
    try:
        event.session[data_models.AppUser]

    except KeyError:
        return None

    return "/"


@rio.page(
    name="Login",
    url_segment="login",
    guard=guard,
)
class LoginPage(rio.Component):
    code: rio.QueryParameter[str] = ""

    @rio.event.on_populate
    async def on_populate(self) -> None:
        if self.code == "":
            return
        
        token = auth.get_access_token(self.code)
        userinfo = auth.fetch_user_info(token)
        user = await self.session[Persistence].find_user_by_email(userinfo["email"])
        if user is None:
            user = data_models.AppUser.new(
                name=userinfo["name"],
                email=userinfo["email"],
            )
            user._id = await self.session[Persistence].insert_user(user)
        self.session.attach(user)
        self.session.navigate_to("/")

    def build(self) -> rio.Component:
        return rio.Card(
            content=rio.Column(
                rio.Spacer(),
                rio.Row(
                    rio.Text(
                        text="Please log in to access Spreadsheet Schema Manager.",
                        style="heading2",
                    ),
                    align_x=0.5,
                ),
                rio.Link(
                    comps.Button(f"Log in via {auth.AUTH_PROVIDER_LABEL} SSO"),
                    auth.get_authorization_url(),
                    align_x=0.5,
                    align_y=0.5,
                ),
                rio.Spacer(),
                spacing=1,
            )
        )
