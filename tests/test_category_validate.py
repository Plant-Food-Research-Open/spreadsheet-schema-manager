import unittest

from spreadsheet_schema_manager_rio import data_models


class TestCategoryValidate(unittest.TestCase):
    def test_no_values_is_valid(self):
        category = data_models.Category()
        self.assertEqual(category.validate(), (True, ""))

    def test_unique_values_is_valid(self):
        category = data_models.Category(values=[
            data_models.Row(header="A"),
            data_models.Row(header="B"),
        ])
        self.assertEqual(category.validate(), (True, ""))

    def test_duplicate_values_is_invalid(self):
        category = data_models.Category(values=[
            data_models.Row(header="A"),
            data_models.Row(header="A"),
            data_models.Row(header="B"),
        ])
        is_valid, message = category.validate()
        self.assertFalse(is_valid)
        self.assertIn("A", message)
        self.assertNotIn("B", message)

    def test_multiple_blank_values_are_flagged_as_duplicate(self):
        category = data_models.Category(values=[
            data_models.Row(header=""),
            data_models.Row(header=""),
        ])
        is_valid, message = category.validate()
        self.assertFalse(is_valid)
        self.assertIn("(blank)", message)

    def test_other_field_types_are_always_valid(self):
        self.assertEqual(data_models.Text().validate(), (True, ""))
        self.assertEqual(data_models.Number().validate(), (True, ""))
        self.assertEqual(data_models.Date().validate(), (True, ""))


if __name__ == '__main__':
    unittest.main()
