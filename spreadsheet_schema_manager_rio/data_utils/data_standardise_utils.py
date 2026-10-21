from typing import Type

import pandas as pd
from pandas.tseries.api import guess_datetime_format

import rio

from .. import data_models
from ..persistence import Persistence


def _non_empty_values(series: pd.Series) -> pd.Series:
    is_empty = series.isna() | (series.astype(str).str.strip() == "")
    return series[~is_empty]


def _guess_date_format_variants(sample: str) -> tuple[str | None, str | None]:
    """
    Guesses a date sample's format under both a month-first and a day-first
    reading, returning (month_first_format, day_first_format).

    guess_datetime_format defaults to month-first when a D/M/Y-style value
    is ambiguous (both fields <=12), so we re-guess with dayfirst=True to get
    the other reading - but only for year-last formats, since applying
    dayfirst to a year-first (ISO) format would wrongly swap day and month
    instead. For unambiguous samples (None, or year-first), both variants are
    the same value.
    """
    month_first_format = guess_datetime_format(sample)
    if not month_first_format or month_first_format.startswith("%Y"):
        return month_first_format, month_first_format

    day_first_format = guess_datetime_format(sample, dayfirst=True) or month_first_format
    return month_first_format, day_first_format


def _format_parses_whole_series(non_empty: pd.Series, date_format: str) -> bool:
    try:
        pd.to_datetime(non_empty, format=date_format, errors='raise')
        return True
    except (ValueError, TypeError):
        return False


def resolve_date_format(series: pd.Series, dayfirst: bool) -> str | None:
    """
    Resolves the concrete source format for this column's values, given a
    dayfirst preference. This is the single place that turns "month-first or
    day-first" into an actual format string - both check_date_format_reliability
    (for display/validation) and standardise_date_column (for the real
    conversion) go through this, so they can never disagree with each other.
    """
    non_empty = _non_empty_values(series)
    if non_empty.empty:
        return None

    month_first_format, day_first_format = _guess_date_format_variants(str(non_empty.iloc[0]))
    return day_first_format if dayfirst else month_first_format


def check_date_format_reliability(series: pd.Series) -> tuple[bool, bool, bool | None]:
    """
    Checks whether this Date column can be reliably standardised, by trying
    both a month-first and a day-first reading of the first non-empty value
    against the whole column.

    Returns (is_reliable, is_ambiguous, dayfirst):
    - is_reliable: True if at least one reading parses every value in the
      column. If False, the column is inconsistent/unparseable under either
      reading (mixed formats, non-date values, etc) and can't be reliably
      standardised.
    - is_ambiguous: True only when both readings parse the whole column but
      disagree with each other, meaning the caller must ask the user which
      one applies rather than assume one.
    - dayfirst: the single reading that actually validated the whole column,
      when unambiguous. None when ambiguous (both readings validate - there's
      no fact-based answer, the caller must pick one) or unreliable (moot -
      no reading validates).
    """
    non_empty = _non_empty_values(series)
    if non_empty.empty:
        return False, False, None

    month_first_format, day_first_format = _guess_date_format_variants(str(non_empty.iloc[0]))
    if month_first_format is None:
        return False, False, None

    month_first_valid = _format_parses_whole_series(non_empty, month_first_format)
    if day_first_format == month_first_format:
        return month_first_valid, False, (False if month_first_valid else None)

    day_first_valid = _format_parses_whole_series(non_empty, day_first_format)
    is_reliable = month_first_valid or day_first_valid
    is_ambiguous = month_first_valid and day_first_valid
    if is_ambiguous or not is_reliable:
        dayfirst = None
    else:
        dayfirst = day_first_valid
    return is_reliable, is_ambiguous, dayfirst


def standardise_date_column(series: pd.Series, date_format: str, dayfirst: bool = True) -> pd.Series:
    """
    Reformats a Date column's values to the given strftime format. Columns
    that aren't reliably parseable (see check_date_format_reliability) are
    left unchanged rather than raising.
    """
    non_empty = _non_empty_values(series)
    if non_empty.empty:
        return series

    detected_format = resolve_date_format(series, dayfirst)
    if not detected_format:
        return series

    try:
        parsed = pd.to_datetime(non_empty, format=detected_format, errors='raise')
    except (ValueError, TypeError):
        return series

    result = series.copy()
    result.loc[parsed.index] = parsed.dt.strftime(date_format)
    return result


def get_unique_new_names(
        existing_names: list[str],
        switch_selections: dict[str, data_models.StandardisationSwitch],
        new_names: dict[str, str] | None = None,
        force_all_unique: bool = True
    ) -> dict[str, str]:
    new_mapping = {}
    existing_name_set = set(existing_names)
    for name, switch in switch_selections.items():
        if switch == data_models.StandardisationSwitch.NEW:
            candidate = new_names[name] if new_names else name
            if force_all_unique:
                while candidate in existing_name_set:
                    candidate += " (new)"
            
            if candidate not in existing_name_set:
                existing_name_set.add(candidate)
                new_mapping[name] = candidate

    return new_mapping


COL_ORIGINAL_COLUMN = "Original Column"
COL_MAPPED_TO = "Mapped To"
COL_FIELD_TYPE = "Field Type"
COL_FIELD_SOURCE = "Field Source"
COL_DATE_ORDER = "Date Order"
COL_ORIGINAL_VALUE = "Original Value"
COL_MAPPED_VALUE = "Mapped Value"
COL_VALUE_SOURCE = "Value Source"

LOG_COLUMNS = [
    COL_ORIGINAL_COLUMN, COL_MAPPED_TO, COL_FIELD_TYPE, COL_FIELD_SOURCE,
    COL_DATE_ORDER, COL_ORIGINAL_VALUE, COL_MAPPED_VALUE, COL_VALUE_SOURCE,
]


def standardise_fields(
        fields: list[data_models.Field],
        df: pd.DataFrame,
        date_format: str,
        all_switch_selections: dict[str, data_models.StandardisationSwitch],
        all_field_selections: dict[str, data_models.Field],
        all_type_selections: dict[str, Type[data_models.Field]],
        all_text_switch_selections: dict[str, dict[str, data_models.StandardisationSwitch]],
        all_text_value_selections: dict[str, dict[str, data_models.Row]],
        all_new_text_values: dict[str, dict[str, str]],
        all_date_dayfirst_selections: dict[str, bool],
    ) -> tuple[pd.DataFrame, list[data_models.Field], list[data_models.Field], pd.DataFrame]:
    df_std = df.copy().fillna("")
    all_fields = []
    updated_fields = []
    log_rows = []
    header_mapping = get_unique_new_names([field.header for field in fields], all_switch_selections)
    for header in df.columns:
        value_mapping = {}
        mapped_field = None
        field_source = (
            "Existing Field" if all_switch_selections[header] == data_models.StandardisationSwitch.EXISTING
            else "New Field"
        )
        if all_switch_selections[header] == data_models.StandardisationSwitch.EXISTING:
            mapped_field = all_field_selections[header]
            if isinstance(mapped_field, data_models.Category):
                value_mapping = get_unique_new_names(
                    existing_names=[row.header for row in mapped_field.values],
                    switch_selections=all_text_switch_selections[header],
                    new_names=all_new_text_values[header],
                    force_all_unique=False,
                )
                if value_mapping:
                    for value, new_value in value_mapping.items():
                        mapped_field.values.append(data_models.Row(header=new_value))
                    updated_fields.append(mapped_field)
                
                for value, switch in all_text_switch_selections[header].items():
                    if switch == data_models.StandardisationSwitch.EXISTING:
                        value_mapping[value] = all_text_value_selections[header][value].header
        else:
            mapped_field = all_type_selections[header]()
            mapped_field.header = header_mapping[header]
            if all_type_selections[header] == data_models.Category:
                value_mapping = get_unique_new_names(
                    existing_names=[],
                    switch_selections=all_text_switch_selections[header],
                    new_names=all_new_text_values[header],
                    force_all_unique=False,
                )
                if value_mapping:
                    for value, new_value in value_mapping.items():
                        mapped_field.values.append(data_models.Row(header=new_value))

            updated_fields.append(mapped_field)
        
        all_fields.append(mapped_field)
        if value_mapping:
            df_std[header] = df_std[header].astype(str).map(value_mapping)

        date_order = ""
        if isinstance(mapped_field, data_models.Date):
            dayfirst = all_date_dayfirst_selections.get(header, True)
            df_std[header] = standardise_date_column(df_std[header], date_format, dayfirst)
            date_order = "Day first" if dayfirst else "Month first"

        log_rows.append({
            COL_ORIGINAL_COLUMN: header,
            COL_MAPPED_TO: mapped_field.header,
            COL_FIELD_TYPE: mapped_field.__class__.__name__,
            COL_FIELD_SOURCE: field_source,
            COL_DATE_ORDER: date_order,
            COL_ORIGINAL_VALUE: "",
            COL_MAPPED_VALUE: "",
            COL_VALUE_SOURCE: "",
        })

        # value_mapping is the fully-resolved raw-value -> final-name mapping
        # actually applied to the data above (post name-collision handling),
        # so logging it here - rather than re-deriving from the raw
        # selections - can't drift from what really happened.
        if isinstance(mapped_field, data_models.Category):
            for raw_value, new_value in value_mapping.items():
                value_source = (
                    "Existing Value"
                    if all_text_switch_selections[header].get(raw_value) == data_models.StandardisationSwitch.EXISTING
                    else "New Value"
                )
                # Column/field info is already recorded on the row above -
                # leave it blank here rather than repeat it on every value.
                log_rows.append({
                    COL_ORIGINAL_COLUMN: "",
                    COL_MAPPED_TO: "",
                    COL_FIELD_TYPE: "",
                    COL_FIELD_SOURCE: "",
                    COL_DATE_ORDER: "",
                    COL_ORIGINAL_VALUE: raw_value,
                    COL_MAPPED_VALUE: new_value,
                    COL_VALUE_SOURCE: value_source,
                })

        df_std.rename(columns={header: mapped_field.header}, inplace=True)

    log_df = pd.DataFrame(log_rows, columns=LOG_COLUMNS)
    return df_std, all_fields, updated_fields, log_df