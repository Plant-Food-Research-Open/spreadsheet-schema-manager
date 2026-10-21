from datetime import date
from typing import Type

import rio

from . import data_models


PAGE_MARGIN_X = 1.0
ICON_BUTTON_SIZE = 2.5
FILTER_TEXT_COLOR = rio.Color.GRAY.darker(0.4)
MAX_CATEGORY_VALUES = 50

_DATE_FORMAT_EXAMPLE = date(2026, 4, 3)

FIELD_TYPES: list[Type[data_models.Field]] = [
    data_models.Category,
    data_models.Measurement,
    data_models.Text,
    data_models.Number,
    data_models.Date,
]

FIELD_TYPE_DICT: dict[str, Type[data_models.Field]] = {
    t.__name__: t for t in FIELD_TYPES
}

MAIN_SECTIONS: list[data_models.MainSection] = [
    data_models.MainSection("Datasets", "material/mist", "/datasets"),
    data_models.MainSection("Workbooks", "material/table_chart", "/workbooks"),
    data_models.MainSection("Templates", "material/backup_table", "/templates"),
    data_models.MainSection("Fields", "material/view_column_2", "/fields"),
]

FOOTER_SECTIONS: list[data_models.MainSection] = [
    data_models.MainSection("Settings", "material/settings", "/settings"),
    data_models.MainSection("Logout", "material/logout", "/logout"),
]

DATE_FORMATS: dict[str, str] = {
    f"YYYY-MM-DD (e.g. {_DATE_FORMAT_EXAMPLE.strftime('%Y-%m-%d')})": "%Y-%m-%d",
    f"DD/MM/YYYY (e.g. {_DATE_FORMAT_EXAMPLE.strftime('%d/%m/%Y')})": "%d/%m/%Y",
    f"DD-MMM-YYYY (e.g. {_DATE_FORMAT_EXAMPLE.strftime('%d-%b-%Y')})": "%d-%b-%Y",
}

DATE_FORMAT_XLSX_NUM_FORMAT: dict[str, str] = {
    "%Y-%m-%d": "yyyy-mm-dd",
    "%d/%m/%Y": "dd/mm/yyyy",
    "%d-%b-%Y": "dd-mmm-yyyy",
}