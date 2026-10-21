from __future__ import annotations
from typing import Type

import rio

from .workbooks_page import WorkbooksPageBase
from .. import auth, data_models
from ..persistence import Persistence, WorkbookPersistence


@rio.page(
    name="Templates",
    url_segment="templates",
    guard=auth.guard,
)
class TemplatesPage(WorkbooksPageBase):
    
    def get_title(self) -> str:
        team = self.session[data_models.AppUser].active_team
        if team is None:
            return "Templates (under your personal space)"
        else:
            return f"Templates (shared under team {team})"

    def get_type(self) -> Type[data_models.Template]:
        return data_models.Template

    def get_persistence(self) -> WorkbookPersistence:
        return self.session[Persistence].get_template()
