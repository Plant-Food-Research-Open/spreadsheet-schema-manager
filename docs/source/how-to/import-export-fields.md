# Import, export and delete Fields in bulk

The **Fields** page has three buttons for working with all your Fields at once: **Export**,
**Import** and **Delete All**. Each acts only on the Fields of the
[space](../getting-started/concepts.md#who-can-see-what) you're working in: your personal space,
or your active team's.

## Export your Fields

Select **Export**. SSM downloads the space's Fields as an Excel file: `Fields.xlsx`, or
`Fields_<team name>.xlsx` in a team's space.

Export is a quick way to back up a set of Fields, review them in Excel, or copy them to another
space or another SSM instance by importing the file there.

## Import Fields from Excel

1. Select **Import** and choose an Excel or CSV file.
2. Read the **Import Summary**. Every Field in the file is listed under one of:
   - **Successfully imported**: added as a new Field.
   - **Errors**: the Field couldn't be read, for example because its type is missing or
     misspelled.
   - **Duplicated and ignored**: a Field with the same header already exists, or the header
     appears more than once in the file.

:::{important}
Import only **adds** Fields. A Field whose header already exists is skipped, not updated. To
replace a Field from a file, delete it first, then import.
:::

The file must use the same layout as an export, so the easiest way to build one is to export
an existing set of Fields and edit it. The layout is described in
[Field import format](../reference/field-import-format.md); for a complete example, download
{download}`Fields.xlsx <../_static/tutorial-data/Fields.xlsx>`, the finished Fields from the
[advanced tutorial](../tutorials/legacy/index.md).

:::{warning}
If the file has a column SSM doesn't recognise, nothing is imported and the summary reports
0 detected fields. Check the column names against the
[import format](../reference/field-import-format.md).
:::

## Delete all your Fields

Select **Delete All** and confirm. This deletes all the space's Fields, for everyone in it,
and can't be undone, so **Export** first if you might want them back.

Deleting a Field doesn't change Templates or Workbooks already built from it: each keeps its
own copy of the Fields it uses.
