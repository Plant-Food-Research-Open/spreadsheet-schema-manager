from __future__ import annotations

import os
import typing as t
from pathlib import Path

import rio

from . import components as comps
from . import data_models, theme
from . import persistence, s3_persistence


def on_app_start(app: rio.App) -> None:
    """
    A function that runs when the app is started.
    """
    # Create a persistence instance. This class hides the gritty details of
    # database interaction from the app.
    mongo_user = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    mongo_pass = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    mongo_app = os.getenv('MONGO_APP')
    mongo_port = os.getenv('MONGO_PORT')
    mongoURL = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_app}:{mongo_port}/"
    pers = persistence.Persistence(mongoURL, "spreadsheet-schema")

    # Now attach it to the session. This way, the persistence instance is
    # available to all components using `self.session[persistence.Persistence]`
    app.default_attachments.append(pers)

    s3_access_key = os.getenv('S3_ACCESS_KEY')
    s3_secret_key = os.getenv('S3_SECRET_KEY')
    connection_string = os.getenv('S3_URL')
    bucket_name = os.getenv('BUCKET_NAME')
    s3 = s3_persistence.S3Persistence(
        access_key=s3_access_key,
        secret_key=s3_secret_key,
        connection_string=connection_string,
        bucket_name=bucket_name,
    )

    app.default_attachments.append(s3)

def on_session_start(sess: rio.Session) -> None:
    pass


# Create the Rio app
app = rio.App(
    name='spreadsheet-schema-manager-rio',
    # "Icon made by zero_wing from www.flaticon.com"
    icon=Path(__file__).parent / "assets" / "audit.png",
    on_app_start=on_app_start,
    # This function will be called each time a user connects
    on_session_start=on_session_start,
    # You can optionally provide a root component for the app. By default,
    # Rio's default navigation is used. By providing your own component, you
    # can create components which stay put while the user navigates between
    # pages, such as a navigation bar or footer.
    #
    # When you do this, make sure your component contains a `rio.PageView`
    # so the currently active page is still visible.
    build=comps.RootComponent,
    # You can also provide a custom theme for the app. This theme will
    # override Rio's default.
    theme=theme.THEME,
    assets_dir=Path(__file__).parent / "assets",
)

