# Field types

Every Field has these properties:

| Property | Meaning |
| --- | --- |
| Header | The column name used in Workbooks and matched against Dataset columns |
| Group | Optional grouping, for organising long Field lists |
| Description | What the column holds |
| Reference URL | Optional link to where the Field is defined in more detail, such as the SOP (standard operating procedure) for a Measurement |

Each type then adds its own:

## Category

A list of allowed text values, each with a name and an optional description. Value names must be
unique within a Field. In a Workbook, a Category column gets a dropdown of its values.

## Measurement

A measured quantity. Its essential properties say what was measured and how:

- **Trait**: what was measured, such as "Weight of a fresh fruit".
- **Unit**: the unit of the values, such as `kg`.
- **Method**: how it was measured, such as "Weigher".

Fill all three in: without them, the numbers can't be interpreted by anyone who wasn't there.
If the method is documented in an SOP, put the SOP's link in **Reference URL**.
You can also add any number of named **parameters**, such as the instrument's model.

## Text

Free text.

## Number

A plain number with no unit, such as a replicate or plot number.

## Date

A calendar date. Dates are standardised to ISO format (`YYYY-MM-DD`). When a Dataset's dates
could be read either day-first or month-first, SSM asks which one is meant.

:::{admonition} Draft
:class: warning
To add: how each type is validated in a generated Workbook.
:::
