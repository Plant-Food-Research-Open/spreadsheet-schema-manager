# Field import format

The file used by **Import** on the Fields page, and produced by **Export**, is a single table
with one block of rows per Field. It's the same layout as the `FieldDefinitions` sheet in
every downloaded Workbook. Download {download}`Fields.xlsx <../_static/tutorial-data/Fields.xlsx>`
for a complete example.

## Columns

Column names are case-insensitive. Any column not listed here makes the whole import fail.

| Column | Used by | Content |
| --- | --- | --- |
| `Header` | All types | The Field's header. A non-empty `Header` starts a new Field. |
| `Group` | All types | Optional group |
| `Type` | All types | `Category`, `Measurement`, `Text`, `Number` or `Date` |
| `Desc` | All types | Optional description |
| `Ref` | All types | Optional Reference URL, such as a link to a Measurement's SOP |
| `Trait` | Measurement | The trait measured |
| `Unit` | Measurement | The unit |
| `Method` | Measurement | The method or instrument |
| `Item_header` | Category | One allowed value |
| `Item_desc` | Category | Optional description of that value |
| `Item_param` | Measurement | A parameter name |
| `Item_value` | Measurement | That parameter's value |

You don't need every column, only the ones your Fields use.

## Layout

Each Field takes one row for its own properties, followed by one row per Category value or
Measurement parameter. On those extra rows, leave `Header` empty and fill only the `Item_`
columns:

| Header | Type | Trait | Unit | Method | Item_header | Item_param | Item_value |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cultivar | Category | | | | | | |
| | | | | | Envy | | |
| | | | | | Gala | | |
| Weight | Measurement | Weight of a fresh fruit | kg | Weigher | | | |
| | | | | | | Scale model | WX-200 |
| Rep | Number | | | | | | |

Here `Cultivar` gets the values Envy and Gala, `Weight` gets one parameter, and `Rep` has no
extra rows.

## How rows are imported

- A Field whose header already exists is skipped, not updated. So is a header that appears
  more than once in the file.
- A Field with a missing or unknown `Type` is reported under **Errors** and not imported.
- Category values must be unique within a Field.

See [Import, export and delete Fields in bulk](../how-to/import-export-fields.md) for the steps.
