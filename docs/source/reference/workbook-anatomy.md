# Anatomy of a Workbook

A downloaded Workbook, or the standardised output of a Dataset, is an Excel file with these
sheets:

`Metadata`
: The Workbook's ID and the Template it came from, if any, plus empty rows for project details: Project
  Title, Project Code, Project Lead, Data Steward, Project Start Date and Project End Date.
  Fill these in so the file still describes itself once it leaves SSM.

`FieldDefinitions`
: Every Field used in the file, in the [Field import format](field-import-format.md). It
  documents what each column means, and you can import it into SSM to recreate the Fields.

`ConstantCategoryFields`
: [Constant Category Fields](../getting-started/concepts.md#constant-category-fields): the
  Category Fields narrowed to a single value in the Workbook, each with its value. They record
  the conditions that were the same for the whole dataset, so the file can later be merged
  with others. By default they're left off the data sheet; the
  [setting](../getting-started/settings.md) "Include constant Category fields" adds them as
  columns.

`RawData`
: The data sheet: one column per Field, in the order chosen before download.
  - Category columns have a dropdown of the allowed values.
  - Date columns are formatted in your [preferred date format](../getting-started/settings.md).
  - For a standardised Dataset, this sheet holds the standardised data. For a new Workbook,
    it's empty, ready to fill in.

`StandardisationLog`
: Standardised Datasets only. One row per original column, showing the Field it was mapped
  to and whether that Field already existed. Category columns are followed by one row per
  original value, showing the value it became. For Date columns, **Date order** records how
  the day/month order was decided:

  | Date order | Meaning |
  | --- | --- |
  | Unambiguous | The dates had no day/month question, such as ISO dates or real Excel dates |
  | Day first (detected) / Month first (detected) | Only one reading fit every value |
  | Day first (selected) / Month first (selected) | Both readings fit, and this is the one you chose |

## QR code list

**Download QRCode**, on the Workbooks page or on the Workbook itself, downloads a separate Excel
file, `<workbook name>_QRCode.xlsx`, for printing QR code labels.

It's for Workbooks with more than one value in at least one Category Field, such as treatments.
The file has a column for each of those Fields and a row for every combination of their
selected values: one row per label to print. For example, with FruitHeight (High, Low) and
Cultivar (Envy, Gala) it lists 4 combinations. Constant Category Fields aren't included, since
they're the same on every label.
