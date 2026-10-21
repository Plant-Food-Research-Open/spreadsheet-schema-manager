import rio

from .workbook_page import WorkbookPageBase
from .. import components as comps
from .. import constants, auth
from ..persistence import Persistence, WorkbookPersistence


@rio.page(
    name="Template",
    url_segment="templates/{param_id}",
    guard=auth.guard,
)
class TemplatePage(WorkbookPageBase):

    def get_title(self) -> str:
        return "Template"
    
    def get_workbook_persistence(self) -> WorkbookPersistence:
        return self.session[Persistence].get_template()

    def build(self) -> rio.Component:
        if self._workbook is None:
            return rio.ProgressCircle(
                align_x=0.5,
                align_y=0.5,
            )
        
        return rio.Column(
            comps.TitleBar(
                page_name=f"Template: {self._workbook.name}",
                buttons=[
                    comps.Button(
                        "Save Template",
                        on_press=self._on_save_button_press,
                    ),
                    comps.Button(
                        "Save Template As...",
                        on_press=self._on_save_as_button_press,
                    ),
                    comps.Button(
                        "Update Fields",
                        on_press=self._on_update_fields_button_press,
                    ),
                ]
            ),
            comps.FilteredFieldSelectionTable(
                fields=self.bind()._fields,
                field_selection=self.bind()._field_selection,
                all_dropdown_selections=self.bind()._all_dropdown_selections,
                grow_y=True,
            ),
            self._banner_factory.build(),
        )
