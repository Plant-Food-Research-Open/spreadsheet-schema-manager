import warnings
import pandas as pd
from pandas.tseries.api import guess_datetime_format

from .. import constants, data_models

warnings.filterwarnings("ignore", category=UserWarning)

# Added to a 0-based pandas row index to get the row number as it appears in
# the source spreadsheet, where row 1 is the header and data starts at row 2.
ROW_NUMBER_OFFSET = 2


def extract_fixed_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts a table starting at [0,0], stopping at the first 
    empty header or first completely empty row.
    """
    # 1. Identify the first 'Unnamed' or NaN column to find the width
    # This identifies the first break in continuous headers
    col_mask = df.columns.to_series().astype(str).str.contains('^Unnamed|^NaN', case=False)
    
    if col_mask.any():
        # Get the index of the first True (the first empty header)
        stop_col_idx = col_mask.values.argmax()
        sub_df = df.iloc[:, :stop_col_idx]
    else:
        sub_df = df

    # 2. Identify the first row that is entirely empty within those columns
    # .all(axis=1) checks if every cell in the row is null
    row_mask = sub_df.isnull().all(axis=1)
    
    if row_mask.any():
        stop_row_idx = row_mask.values.argmax()
        sub_df = sub_df.iloc[:stop_row_idx, :]
        
    return sub_df


def profile_column_types(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    totals_dict = {}
    rows_dict = {}    
    for col in df.columns:
        series = df[col]
        
        # Missing
        is_na = series.isna()
        missing_count = is_na.sum()
        missing_row = ROW_NUMBER_OFFSET + series.index[is_na][0] if missing_count > 0 else ""

        non_na_data = series.dropna()
        
        # Number
        nums = pd.to_numeric(non_na_data, errors='coerce')
        is_num = nums.notna()
        numeric_count = is_num.sum()
        numeric_row = ROW_NUMBER_OFFSET + non_na_data.index[is_num][0] if numeric_count > 0 else ""

        # Date
        remaining_after_nums = non_na_data[nums.isna()]
        dates = pd.to_datetime(remaining_after_nums, format='mixed', errors='coerce')
        is_date = dates.notna()
        date_count = is_date.sum()
        date_row = ROW_NUMBER_OFFSET + remaining_after_nums.index[is_date][0] if date_count > 0 else ""

        # Text/Other
        others = remaining_after_nums[dates.isna()]
        other_count = len(others)
        other_row = ROW_NUMBER_OFFSET + others.index[0] if other_count > 0 else ""
        unique_other_count = others.nunique()

        totals_dict[col] = [
            missing_count, 
            numeric_count, 
            date_count, 
            other_count, 
            unique_other_count
        ]        
        rows_dict[col] = [
            missing_row, 
            numeric_row, 
            date_row, 
            other_row
        ]

    # Return clean dataframes with matching indices (minus the last one for rows)
    df_totals = pd.DataFrame(totals_dict, index=['Missing', 'Number', 'Date', 'Text', 'Unique Texts'])
    df_rows = pd.DataFrame(rows_dict, index=['Missing', 'Number', 'Date', 'Text'])
    return df_totals, df_rows


def validate_date_format(series: pd.Series) -> tuple[str | None, bool]:
    """
    Guesses a date format from the column's first entry and checks it
    against the whole series.

    Returns (detected_format, is_consistent):
    - detected_format: the guessed format, or None if none could be guessed
      from the first entry at all.
    - is_consistent: False only when a format WAS guessed from the first
      entry but other values in the column don't match it - as opposed to
      no format being guessable in the first place, which leaves this True
      even though detected_format is also None in that case.
    """
    series = series.dropna()
    # We "guess" the format of the first entry
    detected_format = guess_datetime_format(str(series.iloc[0]))
    if detected_format is None:
        return None, True

    try:
        # We try to apply that specific format to the entire series
        # If any row doesn't match, it throws an error
        pd.to_datetime(series, format=detected_format, errors='raise')
    except (ValueError, TypeError):
        return None, False

    return detected_format, True


def validate_format(df: pd.DataFrame):
    if df.empty:
        return {
            "status": data_models.DatasetStatus.INVALID,
            "message": "Error: no data found.",
            "errors": {},
            "warnings": {},
            "types": {},
            "profile": {
                "totals": pd.DataFrame(),
                "rows": pd.DataFrame(),
            },
        }

    results = {
        "errors": {},
        "warnings": {},
        "types": {},
        "profile": {
            "totals": pd.DataFrame(),
            "rows": pd.DataFrame(),
        },
    }

    has_errors = False
    has_warnings = False

    # Check for blocking errors

    # Check for warnings
    df_profile_totals, df_profile_rows = profile_column_types(df)
    results["profile"] = {}
    results["profile"]["totals"] = df_profile_totals
    results["profile"]["rows"] = df_profile_rows
    for col in df_profile_totals.columns:
        series = df_profile_totals[col]
        if series['Date'] > 0 and series['Missing'] + series['Date'] == len(df):
            detected_format, is_consistent = validate_date_format(df[col])
            if detected_format is None:
                if is_consistent:
                    results["warnings"][col] = "Unable to detect a date format."
                else:
                    results["warnings"][col] = "Inconsistent date format found."
                has_warnings = True

    for col in df_profile_totals.columns:
        series = df_profile_totals[col]
        type_count = (series[['Number', 'Date', 'Text']] > 0).sum()
        if type_count > 1:
            results["warnings"][col] = "Inconsistent field types found."
            results["types"][col] = "Text"
            has_warnings = True
        elif series['Number'] > 0:
            results["types"][col] = "Measurement or Number"
        elif series['Date'] > 0:
            results["types"][col] = "Date"
        elif series['Unique Texts'] <= constants.MAX_CATEGORY_VALUES:
            results["types"][col] = "Category or Text"
        else:
            results["types"][col] = "Text"
    
    if has_errors:
        results["status"] = data_models.DatasetStatus.INVALID
        results["message"] = "Invalid format, please fix and re-upload."
    elif has_warnings:
        results["status"] = data_models.DatasetStatus.WARNING
        results["message"] = "Inconsistent field formats found, please check for potential typos."
    else:
        results["status"] = data_models.DatasetStatus.READY
        results["message"] = "No obvious errors found, please check the following detected types."
    return results
