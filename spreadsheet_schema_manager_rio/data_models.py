from __future__ import annotations
from abc import ABC, abstractmethod
from collections import Counter

import copy
import enum
import rio

from dataclasses import dataclass, field
from uniserde import ObjectId, as_child

from . import components as comps


class IdMixin:
    @property
    def id(self) -> ObjectId:
        return getattr(self, "_id", None)

    @id.setter
    def id(self, value) -> None:
        self._id = value


class Scope(enum.Enum):
    USER = 1
    TEAM = 2

@dataclass
class AppTeam(IdMixin):
    _id: ObjectId = field(default_factory=ObjectId)
    name: str = ""

    def __str__(self):
        return self.name

@dataclass
class AppUser(IdMixin):
    _id: ObjectId = field(default_factory=ObjectId)
    name: str = ""
    email: str = ""
    joined_teams: list[AppTeam] = field(default_factory=list)
    active_team: AppTeam | None = None
    include_constant_category: bool = False
    date_format: str = "%Y-%m-%d"

    @staticmethod
    def new(name: str, email: str) -> AppUser:
        return AppUser(
            _id=ObjectId(),
            name=name,
            email=email,
        )
    
    def get_owner(self) -> tuple[ObjectId, Scope]:
        if self.active_team is None:
            return (self.id, Scope.USER)
        else:
            return (self.active_team.id, Scope.TEAM)

        
@dataclass
class MainSection:
    main_section_name: str
    icon: str
    target_url: str

@dataclass
class Option:
    name: str = ""
    subname: str = ""
    is_selected: bool = True
    
@dataclass
class DialogItem:
    name: str = ""
    selection: str = ""
    file: rio.FileInfo = None

@dataclass
class Row():
    header: str = ""
    desc: str = ""

@dataclass
class ParamValue():
    param: str = ""
    value: str = ""

@as_child
@dataclass
class Field(IdMixin):
    _id: ObjectId = field(default_factory=ObjectId)
    owner_id: ObjectId = field(default_factory=ObjectId)
    scope: Scope = Scope.USER

    header: str = ""
    group: str = ""
    desc: str = ""
    ref: str = ""
    
    @abstractmethod
    def get_input_component(self) -> comps.FieldInputComponent:
        pass

    def set_owner(self, user: AppUser) -> None:
        self.owner_id, self.scope = user.get_owner()

    def validate(self) -> tuple[bool, str]:
        """
        Checks this Field's current editable state for errors that should
        block saving. Returns (is_valid, error_message) - error_message is
        the full, ready-to-display reason when invalid. Base Field types
        have nothing of their own to validate here.
        """
        return True, ""

@dataclass
class Number(Field):
    def get_input_component(self) -> comps.FieldInputComponent:
        return comps.NumberInputComponent(self)

@dataclass
class Text(Field):
    def get_input_component(self) -> comps.FieldInputComponent:
        return comps.TextInputComponent(self)

@dataclass
class Date(Field):
    def get_input_component(self) -> comps.FieldInputComponent:
        return comps.DateInputComponent(self)

@dataclass
class Category(Field):
    values: list[Row] = field(default_factory=list)

    def get_input_component(self) -> comps.FieldInputComponent:
        return comps.CategoryInputComponent(self)

    def validate(self) -> tuple[bool, str]:
        headers = [row.header for row in self.values]
        counts = Counter(headers)
        duplicates = sorted({header for header in headers if counts[header] > 1})
        if duplicates:
            display_names = [header if header != "" else "(blank)" for header in duplicates]
            return False, f"Duplicate values found: {', '.join(display_names)}. Please make them unique before saving."
        return True, ""

@dataclass
class Measurement(Field):
    trait: str = ""
    unit: str = ""
    method: str = ""
    params: list[ParamValue] = field(default_factory=list)

    def get_input_component(self) -> comps.FieldInputComponent:
        return comps.MeasurementInputComponent(self)

@dataclass
class FieldSelection():
    field_id: ObjectId = field(default_factory=ObjectId)
    value: bool = True

@dataclass
class FieldValueSelection():
    field_id: ObjectId = field(default_factory=ObjectId)
    value: dict[str, bool] = field(default_factory=dict)

    @staticmethod
    def new_empty(field_id: ObjectId, values: list[Row]) -> FieldValueSelection:
        return FieldValueSelection(
            field_id=field_id,
            value={row.header: True for row in values},
        )


@dataclass
class Template(IdMixin):
    _id: ObjectId = field(default_factory=ObjectId)
    owner_id: ObjectId = field(default_factory=ObjectId)
    scope: Scope = Scope.USER

    name: str = ""
    fields: list[Field] = field(default_factory=list)
    field_selection: list[FieldSelection] = field(default_factory=list)
    field_value_selection: list[FieldValueSelection] = field(default_factory=list)

    @staticmethod
    def new_empty(user: AppUser, fields: list[Field]) -> Template:
        owner_id, scope = user.get_owner()
        return Template(
            _id=ObjectId(),
            owner_id=owner_id,
            scope=scope,
            fields=fields.copy(),
            field_selection=[FieldSelection(field.id, False) for field in fields],
            field_value_selection=[FieldValueSelection.new_empty(field.id, field.values) for field in fields if isinstance(field, Category)],
        )
    
    @staticmethod
    def new_from_workbook(workbook: Workbook) -> Template:
        return Template(
            _id=ObjectId(),
            owner_id=workbook.owner_id,
            scope=workbook.scope,
            fields=workbook.fields,
            field_selection=workbook.field_selection,
            field_value_selection=workbook.field_value_selection,
        )

    def copy(self) -> Template:
        return copy.copy(self)

    def get_fields_dict(self) -> dict[ObjectId, Field]:
        return {field.id: field for field in self.fields}

    def get_field_selection_dict(self) -> dict[ObjectId, bool]:
        return {field_selection.field_id: field_selection.value for field_selection in self.field_selection}
    
    def set_field_selection_from_dict(self, dict: dict[ObjectId, bool]) -> None:
        self.field_selection = [FieldSelection(key, value) for key, value in dict.items()]

    def get_all_dropdown_selections_dict(self) -> dict[ObjectId, dict[str, bool]]:
        return {field_value_selection.field_id: field_value_selection.value for field_value_selection in self.field_value_selection}

    def set_field_value_selection_from_dict(self, dict: dict[ObjectId, dict[str, bool]]) -> None:
        self.field_value_selection = [FieldValueSelection(key, value) for key, value in dict.items()]
    
    def update_fields(self, new_fields: list[Field]) -> None:
        field_selection_dict = self.get_field_selection_dict()
        new_field_selection_dict = {}
        for field in new_fields:
            new_field_selection_dict[field.id] = field_selection_dict[field.id] if field.id in field_selection_dict else False
        
        all_dropdown_selections_dict = self.get_all_dropdown_selections_dict()
        new_all_dropdown_selections_dict = {}
        for field in new_fields:
            if field.id in all_dropdown_selections_dict:
                value_selection = all_dropdown_selections_dict[field.id]
                new_value_selection = {}
                for row in field.values:
                    new_value_selection[row.header] = value_selection[row.header] if row.header in value_selection else True
                new_all_dropdown_selections_dict[field.id] = new_value_selection
            elif isinstance(field, Category):
                new_all_dropdown_selections_dict[field.id] = {row.header: True for row in field.values}
        
        self.fields = new_fields
        self.set_field_selection_from_dict(new_field_selection_dict)
        self.set_field_value_selection_from_dict(new_all_dropdown_selections_dict)

    def select_all_fields(self) -> None:
        for field_selection in self.field_selection:
            field_selection.value = True
    
    def get_selected_fields(self) -> list[Field]:
        _fields = self.get_fields_dict()
        return [_fields[field_selection.field_id] for field_selection in self.field_selection if field_selection.value]


@dataclass
class Workbook(Template):
    template_id: ObjectId | None = None
    template_name: str = ""
    field_order: list[ObjectId] = field(default_factory=list)

    @staticmethod
    def new_empty(user: AppUser, fields: list[Field]) -> Workbook:
        template = Template.new_empty(user, fields)
        return Workbook(
            _id=ObjectId(),
            owner_id=template.owner_id,
            scope=template.scope,
            fields=template.fields,
            field_selection=template.field_selection,
            field_value_selection=template.field_value_selection,
            field_order=[field.id for field in fields],
        )
    
    @staticmethod
    def new_from_template(user: AppUser, template: Template) -> Workbook:
        return Workbook(
            _id=ObjectId(),
            owner_id=template.owner_id,
            scope=template.scope,
            fields=template.fields,
            field_selection=template.field_selection,
            field_value_selection=template.field_value_selection,
            template_id=template.id,
            template_name=template.name,
            field_order=[field.id for field in template.fields],
        )
    
    def copy(self) -> Workbook:
        return copy.copy(self)


class DatasetStatus(enum.Enum):
    INVALID = 1
    WARNING = 2
    READY = 3
    COMPLETE = 4

@dataclass
class Dataset(IdMixin):
    _id: ObjectId = field(default_factory=ObjectId)
    owner_id: ObjectId = field(default_factory=ObjectId)
    scope: Scope = Scope.USER
    creator_id: ObjectId = field(default_factory=ObjectId)

    name: str = ""
    status: DatasetStatus = DatasetStatus.READY
    native_date_columns: list[str] = field(default_factory=list)

    @staticmethod
    def new_empty(user: AppUser) -> Dataset:
        owner_id, scope = user.get_owner()
        return Dataset(
            _id=ObjectId(),
            owner_id=owner_id,
            scope=scope,
            creator_id=user.id,
        )
    
    def get_raw_s3_object(self) -> str:
        return f"/{self.scope.name}/{self.owner_id}/{self.creator_id}/{self.id}/raw"
    
    def get_standardised_s3_object(self) -> str:
        return f"/{self.scope.name}/{self.owner_id}/{self.creator_id}/{self.id}/standardised"
    
    def get_standardised_xlsx_s3_object(self) -> str:
        return f"/{self.scope.name}/{self.owner_id}/{self.creator_id}/{self.id}/standardised_xlsx"


class StandardisationSwitch(enum.Enum):
    EXISTING = 1
    NEW = 2
