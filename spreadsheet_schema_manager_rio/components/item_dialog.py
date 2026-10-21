import rio

from .. import components as comps
from .. import constants, data_models
from ..persistence import FieldPersistence, WorkbookPersistence, DatasetPersistence


class SaveDialog():

    @classmethod
    async def create_dialog_item_editor(
        cls, sess: rio.Session, title: str, item: data_models.DialogItem
    ) -> data_models.DialogItem | None:
        """
        ```
        ╔══════════════════════ Card ══════════════════════╗
        ║ ┏━━━━━━━━━━━━━━━━━━━━ Text ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Title                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━ TextInput ━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Name                                         ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━━━ Row ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃   ┏━━━ Button ━━━┓        ┏━━━ Button ━━━┓   ┃ ║
        ║ ┃   ┃ Save         ┃        ┃ Cancel       ┃   ┃ ║
        ║ ┃   ┗━━━━━━━━━━━━━━┛        ┗━━━━━━━━━━━━━━┛   ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ╚══════════════════════════════════════════════════╝
        ```
        """
        def build_dialog_content() -> rio.Component:
            return rio.Column(
                rio.Text(
                    text=title,
                    style="heading2",
                    margin_bottom=1,
                ),
                rio.TextInput(
                    item.name,
                    label="Name",
                    on_change=on_change_name,
                ),
                rio.Row(
                    comps.Button(
                        "Save",
                        on_press=lambda: dialog.close(item),
                    ),
                    comps.Button(
                        "Cancel",
                        on_press=lambda: dialog.close(None),
                        style="minor",
                        color="danger",
                    ),
                    spacing=1,
                    align_x=1,
                ),
                spacing=1,
                align_y=0,
                align_x=0.5,
            )
        
        def on_change_name(ev: rio.TextInputChangeEvent) -> None:
            item.name = ev.text

        dialog = await sess.show_custom_dialog(
            build=build_dialog_content,
            modal=True,
            user_closable=False,
        )

        result = await dialog.wait_for_close()
        return result

    @classmethod
    async def check_name_and_update_status(
        cls,
        item: data_models.DialogItem,
        persistence: WorkbookPersistence,
        banner_factory: comps.BannerFactory,
        parent: rio.Component,
        title: str | None = None,
    ) -> bool:
        if item is None:
            return False
        
        if item.name.strip() == "":
            banner_factory.update(
                parent=parent,
                status='empty',
                name="",
                title=title,
            )
            return False
        
        workbook = await persistence.find_one_by_name(parent.session[data_models.AppUser], item.name)
        if workbook is not None:
            banner_factory.update(
                parent=parent,
                status='already_exists',
                name=item.name,
                title=title,
            )
            return False
        
        return True


class FieldDialog():

    @classmethod
    async def create_dialog_item_editor(
        cls, sess: rio.Session, title: str, item: data_models.DialogItem
    ) -> data_models.DialogItem | None:
        """
        ```
        ╔══════════════════════ Card ══════════════════════╗
        ║ ┏━━━━━━━━━━━━━━━━━━━━ Text ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Title                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━ TextInput ━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Name                                         ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━ Dropdown ━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Items                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━━━ Row ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃   ┏━━━ Button ━━━┓        ┏━━━ Button ━━━┓   ┃ ║
        ║ ┃   ┃ Save         ┃        ┃ Cancel       ┃   ┃ ║
        ║ ┃   ┗━━━━━━━━━━━━━━┛        ┗━━━━━━━━━━━━━━┛   ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ╚══════════════════════════════════════════════════╝
        ```
        """
        def build_dialog_content() -> rio.Component:
            return rio.Column(
                rio.Text(
                    text=title,
                    style="heading2",
                    margin_bottom=1,
                ),
                rio.TextInput(
                    item.name,
                    label="Name",
                    on_change=on_change_name,
                ),
                rio.Dropdown(
                    options={
                        t: t for t in constants.FIELD_TYPE_DICT.keys()
                    },
                    selected_value=data_models.Category.__name__,
                    label="Field type",
                    on_change=on_change_type,
                ),
                rio.Row(
                    comps.Button(
                        "Save",
                        on_press=lambda: dialog.close(item),
                    ),
                    comps.Button(
                        "Cancel",
                        on_press=lambda: dialog.close(None),
                        style="minor",
                        color="danger",
                    ),
                    spacing=1,
                    align_x=1,
                ),
                spacing=1,
                align_y=0,
                align_x=0.5,
            )
        
        def on_change_name(ev: rio.TextInputChangeEvent) -> None:
            item.name = ev.text
        
        def on_change_type(event: rio.DropdownChangeEvent) -> None:
            item.selection = event.value

        dialog = await sess.show_custom_dialog(
            build=build_dialog_content,
            modal=True,
            user_closable=False,
        )

        result = await dialog.wait_for_close()
        return result

    @classmethod
    async def check_name_and_update_status(
        cls,
        item: data_models.DialogItem,
        persistence: FieldPersistence,
        banner_factory: comps.BannerFactory,
        parent: rio.Component,
    ) -> bool:
        if item is None:
            return False
        
        if item.name.strip() == "":
            banner_factory.update(
                parent=parent,
                status='empty',
                name="",
            )
            return False
        
        field = await persistence.find_one_by_header(parent.session[data_models.AppUser], item.name)
        if field is not None:
            banner_factory.update(
                parent=parent,
                status='already_exists',
                name=item.name,
            )
            return False
        
        return True


class FileDialog():

    @classmethod
    async def create_dialog_item_editor(
        cls, sess: rio.Session, title: str, item: data_models.DialogItem
    ) -> data_models.DialogItem | None:
        """
        ```
        ╔══════════════════════ Card ══════════════════════╗
        ║ ┏━━━━━━━━━━━━━━━━━━━━ Text ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Title                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━ FilePickerArea ━━━━━━━━━━━━━━┓ ║
        ║ ┃ Name                                         ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━━━ Row ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃   ┏━━━ Button ━━━┓        ┏━━━ Button ━━━┓   ┃ ║
        ║ ┃   ┃ Save         ┃        ┃ Cancel       ┃   ┃ ║
        ║ ┃   ┗━━━━━━━━━━━━━━┛        ┗━━━━━━━━━━━━━━┛   ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ╚══════════════════════════════════════════════════╝
        ```
        """
        def build_dialog_content() -> rio.Component:
            return rio.Column(
                rio.Text(
                    text=title,
                    style="heading2",
                    margin_bottom=1,
                ),
                rio.FilePickerArea(
                    "Drag & Drop files here",
                    file_types=["xlsx", "xls", "csv"],
                    on_pick_file=on_pick_file,
                ),
                rio.Row(
                    comps.Button(
                        "Save",
                        on_press=lambda: dialog.close(item),
                    ),
                    comps.Button(
                        "Cancel",
                        on_press=lambda: dialog.close(None),
                        style="minor",
                        color="danger",
                    ),
                    spacing=1,
                    align_x=1,
                ),
                spacing=1,
                align_y=0,
                align_x=0.5,
            )
        
        async def on_pick_file(ev: rio.FilePickEvent) -> None:
            item.name = ev.file.name
            item.file = ev.file            
                    
        dialog = await sess.show_custom_dialog(
            build=build_dialog_content,
            modal=True,
            user_closable=False,
        )

        result = await dialog.wait_for_close()
        return result

    @classmethod
    async def check_name_and_update_status(
        cls,
        item: data_models.DialogItem,
        persistence: DatasetPersistence,
        banner_factory: comps.BannerFactory,
        parent: rio.Component,
    ) -> bool:
        if item is None:
            return False
        
        if item.name.strip() == "":
            banner_factory.update(
                parent=parent,
                status='empty',
                name="",
            )
            return False
        
        dataset = await persistence.find_one_by_name(parent.session[data_models.AppUser], item.name)
        if dataset is not None:
            banner_factory.update(
                parent=parent,
                status='already_exists',
                name=item.name,
            )
            return False
        
        return True


class DropdownDialog():

    @classmethod
    async def create_dialog_item_editor(
        cls, sess: rio.Session, title: str, item: data_models.DialogItem, options: list[str]
    ) -> data_models.DialogItem | None:
        """
        ```
        ╔══════════════════════ Card ══════════════════════╗
        ║ ┏━━━━━━━━━━━━━━━━━━━━ Text ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Title                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━ Dropdown ━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Items                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━━━ Row ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃              ┏━━━ Button ━━━┓                ┃ ║
        ║ ┃              ┃ Ok           ┃                ┃ ║
        ║ ┃              ┗━━━━━━━━━━━━━━┛                ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ╚══════════════════════════════════════════════════╝
        ```
        """
        def build_dialog_content() -> rio.Component:
            return rio.Column(
                rio.Text(
                    text=title,
                    style="heading2",
                    margin_bottom=1,
                ),
                rio.Dropdown(
                    options=options,
                    selected_value=options[0],
                    on_change=on_change_type,
                ),
                rio.Row(
                    comps.Button(
                        "Ok",
                        on_press=lambda: dialog.close(item),
                    ),
                    align_x=0.5,
                ),
                spacing=1,
                align_y=0,
                align_x=0.5,
            )
                
        def on_change_type(event: rio.DropdownChangeEvent) -> None:
            item.selection = event.value

        dialog = await sess.show_custom_dialog(
            build=build_dialog_content,
            modal=True,
            user_closable=False,
        )

        result = await dialog.wait_for_close()
        return result


class TextDialog():

    @classmethod
    async def create_dialog_item_editor(
        cls, sess: rio.Session, title: str
    ) -> None:
        """
        ```
        ╔══════════════════════ Card ══════════════════════╗
        ║ ┏━━━━━━━━━━━━━━━━━━━━ Text ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃ Title                                        ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ║ ┏━━━━━━━━━━━━━━━━━━━━━ Row ━━━━━━━━━━━━━━━━━━━━┓ ║
        ║ ┃              ┏━━━ Button ━━━┓                ┃ ║
        ║ ┃              ┃ Ok           ┃                ┃ ║
        ║ ┃              ┗━━━━━━━━━━━━━━┛                ┃ ║
        ║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
        ╚══════════════════════════════════════════════════╝
        ```
        """
        def build_dialog_content() -> rio.Component:
            return rio.Column(
                rio.Text(
                    text=title,
                    style="heading3",
                    overflow="wrap",
                    margin_bottom=1,
                    min_width=35,
                ),
                rio.Row(
                    comps.Button(
                        "Ok",
                        on_press=lambda: dialog.close(None),
                    ),
                    align_x=0.5,
                ),
                spacing=1,
                align_y=0,
                align_x=0.5,
            )
        
        dialog = await sess.show_custom_dialog(
            build=build_dialog_content,
            modal=True,
            user_closable=False,
        )

        result = await dialog.wait_for_close()
        return result