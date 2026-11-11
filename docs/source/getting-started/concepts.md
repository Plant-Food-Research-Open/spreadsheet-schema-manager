# Concepts

SSM is built around four objects. Fields are the building blocks; the other three either
group Fields or are checked against them.

Field
: One column definition: its header, a description, an optional group and reference URL, and a
  type. Fields are reused across Templates, Workbooks and Datasets, which is what keeps
  column names and values consistent.

Workbook
: A selection of Fields, and of Category values, that downloads as an Excel file with
  headers filled in and data validation (such as dropdowns for Category values) applied,
  ready for someone to collect data in.

Template
: Optional. A saved selection of Fields and Category values to start new Workbooks from,
  which is useful when you create similar Workbooks repeatedly, such as one per season. A
  Workbook created from a Template copies its selections, and you can still change them
  afterwards.

Dataset
: An existing spreadsheet you upload, to be standardised against your Fields. Each column is
  mapped to an existing Field or used to create a new one, and each Category value is mapped
  to an existing value or added as a new one.

## Field types

| Type | Use it for | Type-specific properties |
| --- | --- | --- |
| Category | A fixed list of allowed text values, such as cultivar names | The list of values, each with an optional description |
| Measurement | A measured quantity | Trait, unit and method, which together say what was measured and how; plus optional named parameters |
| Text | Free text, such as comments | None |
| Number | A plain number, such as a replicate number | None |
| Date | A calendar date | None; standardised to ISO format, `YYYY-MM-DD`, by default |

See [Field types](../reference/field-types.md) for details.

## Constant Category Fields

An experiment's spreadsheet usually records only what varies: if every apple tree in a
trial is Gala, there's no Cultivar column, because a column holding the same value on every row looks
useless. The constant conditions get written down somewhere else, typically in the final
report.

That works for one dataset on its own, but it breaks when you later want to combine several.
A trial that recorded only Gala and another that recorded Gala and Envy can't be merged
reliably if the first file never says it was Gala. Once the constant values are missing from
the data, there's no reliable way to tell how the rows of the different datasets line up.

SSM treats these constant values as data. When a Workbook narrows a Category Field down to a
single value, that Field becomes a **constant Category Field**. The single value can be set on
the Workbook itself or come from the Template it was created from. The downloaded file records
the Field, with its value, on its own `ConstantCategoryFields` sheet. The data sheet stays free of repeated
values, and the constants still travel with the data instead of living only in a report.
When you do need them as ordinary columns, for example to merge files, turn on the
[setting](settings.md) that adds them to the data sheet.

## Who can see what

You always work in one **space**: your personal space, or a team's shared space. Each page's
heading tells you which, for example "Fields (under your personal space)" or
"Fields (shared under team Orchard)".

Fields, Templates and Workbooks
: Belong to the space they were created in. In your personal space, only you see them. In a
  team's space, every member of the team sees and edits the same ones, which is how a team
  keeps one shared schema.

Datasets
: Always personal: only the person who uploaded a Dataset can see it, even in a team's space.
  It's still listed only in the space it was uploaded in, and it's standardised against that
  space's Fields. So several team members can standardise their own spreadsheets against the
  team's Fields without seeing each other's data.

To work in a team's space, choose it as your **Current active team** in
[Settings](settings.md). You can only choose teams you've been added to.

:::{note}
For now, teams are created, and members added, by your SSM administrator. A screen for
managing teams in SSM itself is planned.
:::
