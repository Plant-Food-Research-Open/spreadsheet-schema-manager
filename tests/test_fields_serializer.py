import unittest

from pathlib import Path
import pandas as pd
from spreadsheet_schema_manager_rio.data_utils.fields_serializer import FieldsSerializer
from spreadsheet_schema_manager_rio import data_models

DATA_DIR = Path(__file__).parent / "fields_serializer"

class TestFieldsSerializer(unittest.TestCase):
    def deserialize_fields_from_df(self, df: pd.DataFrame, expected_fields: list[data_models.Field]) -> tuple[list[data_models.Field], list[str]]:
        actual_fields, detected_headers = FieldsSerializer.deserialize_fields_from_df(df)
        for expected_field, actual_field in zip(expected_fields, actual_fields):
            actual_field.id = expected_field.id
            actual_field.owner_id = expected_field.owner_id
            actual_field.scope = expected_field.scope
        return actual_fields, detected_headers

    def test_empty(self):
        fields = []
        expected_df = pd.DataFrame()
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        # print(expected_df.to_csv())
        # print(actual_df.to_csv())
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)

    def test_one_text(self):
        fields = [
            data_models.Text(
                header="test",
                group="group",
                desc="desc",
                ref="ref",
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "one_text.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)
    
    def test_simple(self):
        fields = [
            data_models.Text(
                header="test1",
                group="group",
                desc="desc",
                ref="ref",
            ),
            data_models.Number(
                header="test2",
                group="",
                desc="",
                ref="",
            ),
            data_models.Date(
                header="test3",
                group="group",
                desc="desc",
                ref="ref",
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "simple.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)
    
    def test_measurement(self):
        fields = [
            data_models.Measurement(
                header="test",
                trait="1",
                unit="2",
                method="3",
                params=[
                    data_models.ParamValue(param="p1", value="v1"),
                    data_models.ParamValue(param="p2", value="v2"),
                    data_models.ParamValue(param="p3", value="v3"),
                ]
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "measurement.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)
    
    def test_measurement_empty(self):
        fields = [
            data_models.Measurement(
                header="test",
                trait="1",
                unit="2",
                method="3",
                params=[]
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "measurement_empty.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)
        
    def test_category(self):
        fields = [
            data_models.Category(
                header="test",
                values=[
                    data_models.Row(header="h1", desc="d1"),
                    data_models.Row(header="h2", desc="d2"),
                ]
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "category.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)
    
    def test_category_empty(self):
        fields = [
            data_models.Category(
                header="test",
                values=[]
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "category_empty.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)
    
    def test_category_value_desc_empty(self):
        fields = [
            data_models.Category(
                header="test",
                values=[
                    data_models.Row(header="h1", desc="d1"),
                    data_models.Row(header="h2"),
                ]
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "category_value_desc_empty.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)

    def test_mix(self):
        fields = [
            data_models.Category(
                header="test1",
                values=[
                    data_models.Row(header="h1", desc="d1"),
                    data_models.Row(header="h2", desc="d2"),
                ]
            ),
            data_models.Measurement(
                header="test2",
                trait="1",
                unit="2",
                method="3",
                params=[
                    data_models.ParamValue(param="p1", value="v1"),
                    data_models.ParamValue(param="p2", value="v2"),
                    data_models.ParamValue(param="p3", value="v3"),
                ]
            ),
            data_models.Text(
                header="test3",
                group="group",
                desc="desc",
                ref="ref",
            ),
        ]
        expected_df = pd.read_csv(DATA_DIR / "mix.csv", keep_default_na=False, dtype=str)
        actual_df = FieldsSerializer.serialize_fields_to_df(fields)
        self.assertEqual(expected_df.to_csv(), actual_df.to_csv())

        actual_fields, detected_headers = self.deserialize_fields_from_df(expected_df, fields)
        self.assertEqual(fields, actual_fields)


if __name__ == '__main__':
    unittest.main()
