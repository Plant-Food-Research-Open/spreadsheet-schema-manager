import unittest

import pandas as pd

from spreadsheet_schema_manager_rio import data_models
from spreadsheet_schema_manager_rio.data_models import StandardisationSwitch
from spreadsheet_schema_manager_rio.data_utils.data_standardise_utils import (
    check_date_format_reliability,
    resolve_date_format,
    standardise_date_column,
    standardise_fields,
)


class TestCheckDateFormatReliability(unittest.TestCase):
    def test_iso_format(self):
        series = pd.Series(["2024-04-03", "2024-05-06"])
        self.assertEqual(check_date_format_reliability(series), (True, False, False))

    def test_month_first_only(self):
        # Row 1's day=25 rules out a day-first reading for the whole column.
        series = pd.Series(["03/04/2024", "06/25/2024"])
        self.assertEqual(check_date_format_reliability(series), (True, False, False))

    def test_day_first_only(self):
        # Row 1's day=25 rules out a month-first reading for the whole column.
        series = pd.Series(["03/04/2024", "25/06/2024"])
        self.assertEqual(check_date_format_reliability(series), (True, False, True))

    def test_ambiguous(self):
        series = pd.Series(["03/04/2024", "05/06/2024"])
        self.assertEqual(check_date_format_reliability(series), (True, True, None))

    def test_unreliable(self):
        series = pd.Series(["03/04/2024", "not-a-date"])
        self.assertEqual(check_date_format_reliability(series), (False, False, None))

    def test_empty_column(self):
        series = pd.Series(["", None, ""])
        self.assertEqual(check_date_format_reliability(series), (False, False, None))


class TestResolveDateFormat(unittest.TestCase):
    def test_ambiguous_sample_differs_by_dayfirst(self):
        series = pd.Series(["03/04/2024"])
        self.assertEqual(resolve_date_format(series, dayfirst=True), "%d/%m/%Y")
        self.assertEqual(resolve_date_format(series, dayfirst=False), "%m/%d/%Y")

    def test_iso_sample_ignores_dayfirst(self):
        series = pd.Series(["2024-04-03"])
        self.assertEqual(resolve_date_format(series, dayfirst=True), "%Y-%m-%d")
        self.assertEqual(resolve_date_format(series, dayfirst=False), "%Y-%m-%d")

    def test_empty_column_returns_none(self):
        series = pd.Series(["", None])
        self.assertIsNone(resolve_date_format(series, dayfirst=True))


class TestStandardiseDateColumn(unittest.TestCase):
    def test_day_first_column(self):
        series = pd.Series(["03/04/2024", "25/06/2024"])
        actual = standardise_date_column(series, "%Y-%m-%d", dayfirst=True)
        self.assertEqual(actual.tolist(), ["2024-04-03", "2024-06-25"])

    def test_month_first_only_column_with_dayfirst_false(self):
        # dayfirst=False must be honoured here rather than defaulting to
        # day-first, which would fail to parse row 1 and silently no-op.
        series = pd.Series(["03/04/2024", "06/25/2024"])
        actual = standardise_date_column(series, "%Y-%m-%d", dayfirst=False)
        self.assertEqual(actual.tolist(), ["2024-03-04", "2024-06-25"])

    def test_unreliable_column_left_unchanged(self):
        series = pd.Series(["03/04/2024", "not-a-date"])
        actual = standardise_date_column(series, "%Y-%m-%d", dayfirst=True)
        self.assertEqual(actual.tolist(), series.tolist())

    def test_custom_output_format(self):
        series = pd.Series(["2024-04-03"])
        actual = standardise_date_column(series, "%d/%m/%Y", dayfirst=True)
        self.assertEqual(actual.tolist(), ["03/04/2024"])


class TestStandardiseFields(unittest.TestCase):
    def test_new_date_and_text_fields(self):
        df = pd.DataFrame({
            "Date Column": ["03/04/2024", "25/06/2024"],
            "Text Column": ["a", "b"],
        })
        all_switch_selections = {
            "Date Column": StandardisationSwitch.NEW,
            "Text Column": StandardisationSwitch.NEW,
        }
        all_type_selections = {
            "Date Column": data_models.Date,
            "Text Column": data_models.Text,
        }
        empty_selections = {"Date Column": {}, "Text Column": {}}

        df_std, all_fields, updated_fields, log_df = standardise_fields(
            [],
            df,
            "%Y-%m-%d",
            all_switch_selections,
            {},
            all_type_selections,
            empty_selections,
            empty_selections,
            empty_selections,
            {"Date Column": True},
        )

        self.assertEqual(df_std["Date Column"].tolist(), ["2024-04-03", "2024-06-25"])
        self.assertEqual(df_std["Text Column"].tolist(), ["a", "b"])
        self.assertEqual([type(f) for f in all_fields], [data_models.Date, data_models.Text])

        self.assertEqual(log_df["Original Column"].tolist(), ["Date Column", "Text Column"])
        self.assertEqual(log_df["Field Source"].tolist(), ["New Field", "New Field"])
        self.assertEqual(log_df["Date Order"].tolist(), ["Day first", ""])

    def test_category_value_mappings_are_logged(self):
        df = pd.DataFrame({"Grade": ["A", "B", "A"]})
        all_switch_selections = {"Grade": StandardisationSwitch.NEW}
        all_type_selections = {"Grade": data_models.Category}
        all_text_switch_selections = {
            "Grade": {"A": StandardisationSwitch.NEW, "B": StandardisationSwitch.NEW},
        }
        all_new_text_values = {"Grade": {"A": "Grade A", "B": "Grade B"}}

        _, _, _, log_df = standardise_fields(
            [],
            df,
            "%Y-%m-%d",
            all_switch_selections,
            {},
            all_type_selections,
            all_text_switch_selections,
            {"Grade": {}},
            all_new_text_values,
            {},
        )

        value_rows = log_df[log_df["Original Value"] != ""]
        self.assertEqual(value_rows["Original Value"].tolist(), ["A", "B"])
        self.assertEqual(value_rows["Mapped Value"].tolist(), ["Grade A", "Grade B"])
        self.assertEqual(value_rows["Value Source"].tolist(), ["New Value", "New Value"])

        # Column/field info is already on the column-level row above these -
        # left blank here instead of repeating it on every value.
        for col in ["Original Column", "Mapped To", "Field Type", "Field Source", "Date Order"]:
            self.assertEqual(value_rows[col].tolist(), ["", ""])


if __name__ == '__main__':
    unittest.main()
