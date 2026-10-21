import os
from io import BytesIO
import pandas as pd

import rio

from .. import components as comps
from .. import constants, data_models


async def create_dialog_and_read_df(
        title: str,
        sess: rio.Session,
        banner_factory: comps.BannerFactory,
        parent: rio.Component
    ) -> tuple[data_models.DialogItem | None, pd.DataFrame | None]:
    new_item = await comps.FileDialog.create_dialog_item_editor(
        sess=sess,
        title=title,
        item=data_models.DialogItem(),
    )

    if new_item is None or new_item.name.strip() == "":
        banner_factory.update(
            parent=parent,
            status='empty',
            title="File",
        )
        return None, None

    base, ext = os.path.splitext(new_item.name)
    ext = ext.lower()
    new_item.name = base
    file_obj = await new_item.file.open('rb')
    df = pd.DataFrame()
    try:
        if ext in ('.xls', '.xlsx'):
            sheets = pd.read_excel(file_obj, sheet_name=None)
            if len(sheets) == 1:
                df, = sheets.values()
            else:
                options = list(sheets.keys())
                sheet_item = await comps.DropdownDialog.create_dialog_item_editor(
                    sess=sess,
                    title="Select sheet",
                    item=data_models.DialogItem(selection=options[0]),
                    options=options,
                )
                new_item.name = f"{base}_{sheet_item.selection}"
                df = sheets[sheet_item.selection]
        elif ext == '.csv':
            df = pd.read_csv(file_obj)
        else:
            raise Exception("Invalid file format.")

        file_obj.close()
    except:
        banner_factory.update(
            parent=parent,
            status='not_xls',
            name=f"{base}{ext}",
        )
        return None, None
    
    return new_item, df