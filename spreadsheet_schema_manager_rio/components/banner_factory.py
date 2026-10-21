from typing import Literal

import rio


class BannerFactory():
    def __init__(
        self,
        title: str = "Workbook",
    ) -> None:
        self.title = title

    title: str = "Workbook"
    text: str = ""
    style: Literal['info', 'success', 'warning', 'danger'] = 'success'

    def update(
            self,
            parent: rio.Component,
            status: Literal['success', 'already_exists', 'empty', 'created', 'deleted', 'renamed', 'updated', 'duplicate_map', 'empty_category_field', 'delete_all', 'invalid'],
            name: str | None = None,
            title: str | None = None,            
        ):
        if title is None:
            title = self.title
        
        match status:
            case 'success':
                self.text = f"{title} {name} saved successfully."
                self.style = 'success'
            case 'already_exists':
                self.text = f"{title} {name} already exists!"
                self.style = 'danger'
            case 'empty':
                self.text = f"{title} name was not entered!"
                self.style = 'danger'
            case 'created':
                self.text = f"{title} {name} created successfully."
                self.style = 'success'
            case 'deleted':
                self.text = f"{title} {name} deleted successfully."
                self.style = 'success'
            case 'renamed':
                self.text = f"{title} {name} renamed successfully."
                self.style = 'success'
            case 'updated':
                self.text = f"{title} updated successfully."
                self.style = 'success'
            case 'not_xls':
                self.text = f"{name} is not a spreadsheet."
                self.style = 'danger'
            case 'uploaded':
                self.text = f"{title} {name} uploaded successfully."
                self.style = 'success'
            case 'duplicate_map':
                self.text = f"Multiple headers are being mapped to Field {name}."
                self.style = 'danger'
            case 'empty_category_field':
                self.text = f"Unable to map to Field {name} with empty category values."
                self.style = 'danger'
            case 'delete_all':
                self.text = f"All {title}s deleted successfully."
                self.style = 'success'
            case 'invalid':
                self.text = name
                self.style = 'danger'

        parent.force_refresh()
    
    def clear(self, parent: rio.Component):
        self.text = ""
        self.style = 'success'
        parent.force_refresh()

    def build(self) -> rio.Component:
        # Screen readers announce "alert" regions immediately and "status"
        # regions politely; map our banner styles onto those implicit
        # aria-live semantics so status updates get announced without a
        # separate live region. Only assign a role once there's actually a
        # message: an empty live region has nothing to announce and
        # shouldn't be exposed as one.
        role = None
        if self.text:
            role = "alert" if self.style in ("danger", "warning") else "status"
        return rio.Banner(
            text=self.text,
            style=self.style,
            accessibility_role=role,
        )
