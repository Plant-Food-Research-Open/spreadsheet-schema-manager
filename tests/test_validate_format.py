import unittest

from pathlib import Path
import pandas as pd
from spreadsheet_schema_manager_rio.data_utils.data_clean_utils import validate_format
from spreadsheet_schema_manager_rio.data_models import DatasetStatus

DATA_DIR = Path(__file__).parent / "validate_format"

class TestValidateFormat(unittest.TestCase):
    def test_clean(self):
        expected = {
            'errors': {},
            'warnings': {},
            'types': {'A': 'Measurement or Number', 'B': 'Category or Text', 'C': 'Date'},
            'status': DatasetStatus.READY
        }
        df = pd.read_csv(DATA_DIR / "clean.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())
    
    def test_category_or_text(self):
        expected = {
            'errors': {},
            'warnings': {},
            'types': {'A': 'Category or Text', 'B': 'Text'},
            'status': DatasetStatus.READY
        }
        df = pd.read_csv(DATA_DIR / "category_or_text.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())

    def test_empty_file(self):
        expected = {
            'errors': {},
            'warnings': {},
            'status': DatasetStatus.INVALID,
            'message': 'Error: no data found.'
        }
        df = pd.read_csv(DATA_DIR / "empty.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())

    def test_missing_value(self):
        expected = {
            'errors': {},
            'warnings': {},
            'status': DatasetStatus.READY
        }
        df = pd.read_csv(DATA_DIR / "missing.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())

    def test_empty_column(self):
        expected = {
            'errors': {},
            'warnings': {},
            'status': DatasetStatus.READY
        }
        df = pd.read_csv(DATA_DIR / "empty_column.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())

    def test_inconsistent_types(self):
        expected = {
            'errors': {},
            'warnings': {
                'A': 'Inconsistent field types found.',
                'C': 'Inconsistent field types found.'
            },
            'status': DatasetStatus.WARNING
        }
        df = pd.read_csv(DATA_DIR / "mix_types.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())

    def test_inconsistent_dates(self):
        expected = {
            'errors': {},
            'warnings': {
                'C': 'Inconsistent date format found.'
            },
            'status': DatasetStatus.WARNING
        }
        df = pd.read_csv(DATA_DIR / "mix_dates.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())

    def test_undetectable_date_format(self):
        # A 2-digit year (e.g. "1/5/26") is internally consistent but
        # guess_datetime_format can't guess any format for it at all - this
        # must be reported distinctly from a genuine row-to-row mismatch.
        expected = {
            'errors': {},
            'warnings': {
                'C': 'Unable to detect a date format.'
            },
            'status': DatasetStatus.WARNING
        }
        df = pd.read_csv(DATA_DIR / "two_digit_year.csv")
        actual = validate_format(df)
        self.assertTrue(expected.items() <= actual.items())


if __name__ == '__main__':
    unittest.main()
