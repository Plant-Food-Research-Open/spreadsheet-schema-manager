from collections.abc import Callable
from collections import Counter

import rio
import functools
from bson import ObjectId

from .. import components as comps
from .. import constants, data_models
from .table_filter import FilterRow


class FieldTable(comps.CustomTable[data_models.Field]):
    on_delete_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_rename_button_press: Callable[[ObjectId, str], None] = lambda: None

    def __post_init__(self) -> None:
        self.min_widths = [0, 0, 10, 15, 0]

    def build_header(self) -> list[rio.Component]:
        return [
            rio.Row(comps.BoldText("Group")),
            rio.Row(comps.BoldText("Type")),
            rio.Row(comps.BoldText("Name")),
            rio.Row(comps.BoldText("Description")),
            rio.Row(comps.BoldText("Actions")),
        ]

    def build_row(self, field: data_models.Field) -> list[rio.Component]:
        return [
            rio.Text(
                field.group,
                align_x=0,
            ),
            rio.Text(
                field.__class__.__name__,
                align_x=0,
            ),
            rio.Link(
                rio.Text(
                    field.header,
                    fill=self.session.theme.secondary_color,
                    underlined=True,
                    overflow='ellipsize',
                ),
                f"/fields/{field.id}",
            ),
            rio.Text(
                field.desc,
                overflow='ellipsize',
            ),
            rio.Row(
                comps.Button(
                    "Rename",
                    on_press=functools.partial(self.on_rename_button_press, field.id, field.header),
                    style="minor",
                    accessibility_label=f"Rename {field.header}",
                ),
                rio.Spacer(),
                rio.IconButton(
                    "material/delete",
                    min_size=constants.ICON_BUTTON_SIZE,
                    margin_right=0.5,
                    color="danger",
                    on_press=functools.partial(self.on_delete_button_press, field.id, field.header),
                    accessibility_label=f"Delete {field.header}",
                ),
                spacing=0.5,
            ),
        ]


class FilteredFieldBase(rio.Component):
    """Base class for filtered field table components with common filtering logic."""
    fields: list[data_models.Field] = []

    _group_options: list[data_models.Option] = []
    _option_map: dict = {"": "(Unassigned)"}
    _inv_option_map: dict = {v: k for k, v in _option_map.items()}

    _type_options: list[data_models.Option] = []

    _group_counter: Counter = Counter()
    _type_counter: Counter = Counter()
    
    @rio.event.on_populate
    def on_populate(self) -> None:
        group_set = {field.group for field in self.fields if field.group}
        groups = sorted(list(group_set))
        groups.append(self._option_map.get("", ""))
        self._group_options = [data_models.Option(name=group, is_selected=True) for group in groups]
        self._type_options: list[data_models.Option] = [data_models.Option(name=t.__name__, is_selected=True) for t in constants.FIELD_TYPES]

        self._group_counter = Counter(self._option_map.get(field.group, field.group) for field in self.fields)
        self._type_counter = Counter(field.__class__.__name__ for field in self.fields)

    def on_change_selection(self, option: data_models.Option) -> None:
        option.is_selected = not option.is_selected
        self.force_refresh()

    def filter_fields(self) -> list[data_models.Field]:
        fields_filtered = []
        selected_groups = [
            self._inv_option_map.get(option.name, option.name) for option in self._group_options if option.is_selected
        ]
        selected_types = [
            option.name for option in self._type_options if option.is_selected
        ]
        for field in self.fields:
            if field.group in selected_groups and field.__class__.__name__ in selected_types:
                fields_filtered.append(field)
        return fields_filtered


class FilteredFieldTable(FilteredFieldBase):
    on_new_button_press: Callable[[], None] = lambda: None
    on_delete_button_press: Callable[[ObjectId, str], None] = lambda: None
    on_rename_button_press: Callable[[ObjectId, str], None] = lambda: None

    @rio.event.on_populate
    def on_populate(self) -> None:
        for option in self._group_options:
            option.subname = f"({self._group_counter.get(option.name, 0)})"
        for option in self._type_options:
            option.subname = f"({self._type_counter.get(option.name, 0)})"

    def build(self) -> rio.Component:
        fields_filtered = self.filter_fields()

        return rio.Column(
            FilterRow(
                group_options=self.bind()._group_options,
                type_options=self.bind()._type_options,
                on_change_status=self.on_change_selection,
                on_new_button_press=self.on_new_button_press,
                add_button_label="Add field",
            ),
            rio.ScrollContainer(
                rio.Column(
                    FieldTable(
                        rows=fields_filtered,
                        on_delete_button_press=self.on_delete_button_press,
                        on_rename_button_press=self.on_rename_button_press,
                        grow_y=True,
                    ),
                    spacing=0.5,
                    align_y=0,
                ),
                margin=constants.PAGE_MARGIN_X,
                grow_y=True,
            ),
        )