# From legacy spreadsheets to a shared schema

This advanced tutorial follows one realistic job from start to finish. You have two
spreadsheets from fruit assessments, recorded in different seasons by different people. They
hold the same kind of data but use different column names, spellings and codes. You'll use
SSM to bring them into one shared schema.

New to SSM? Do [Your first Workbook](../first-workbook.md) and
[Reuse a setup with Templates](../templates.md) first.

```{toctree}
:maxdepth: 1
:hidden:

01-upload-and-check
02-draft-fields
03-fit-second-dataset
04-curate-fields
05-standardise
06-collect-next-season
```

## Chapters

1. [Upload and check a spreadsheet](01-upload-and-check.md), and fix a data error.
2. [First pass: draft Fields](02-draft-fields.md) from the first spreadsheet.
3. [First pass: fit the second spreadsheet](03-fit-second-dataset.md) into those Fields,
   deciding on the naming as you go.
4. [Curate the Fields](04-curate-fields.md) into a final, shared schema.
5. [Second pass: standardise](05-standardise.md) both spreadsheets against the final Fields.
6. [Collect next season's data](06-collect-next-season.md) to the same standard from the start.

:::{important}
The **first pass** (chapters 2 and 3) only shapes your Fields. The standardised files you keep
come from the **second pass** (chapter 5), once the Fields are final. Expect to standardise
each spreadsheet twice.
:::

## Before you start: start with no Fields

The tutorial assumes your space has no Fields to begin with. Existing Fields would change what
SSM suggests in every standardisation step, so your screens wouldn't match the tutorial's.

If you already have Fields, set them aside first:

1. Make sure you're in your **personal space**. Check the Fields page heading: it should say
   "Fields (under your personal space)". If it names a team, clear **Current active team** in
   [Settings](../../getting-started/settings.md) first: the next step would delete the team's
   Fields for everyone in it.
2. On the Fields page, select **Export** and keep the downloaded `Fields.xlsx`.
3. Select **Delete All** and confirm.

When you've finished the tutorial, restore them: select **Delete All** to remove the
tutorial's Fields, then **Import** your saved file. See
[Import, export and delete Fields in bulk](../../how-to/import-export-fields.md).

:::{warning}
Templates and Workbooks recognise Fields by an internal ID, not by name, and restored Fields get
new IDs. Your existing Templates and Workbooks keep working, because each keeps its own copy of
its Fields. But if you later select **Update Fields** on one of them, the restored Fields come
in as new: unticked, with all their values selected. Tick them again, and re-narrow any values,
before saving.
:::

## There's rarely one right answer

Most decisions in this tutorial are judgment calls: which name to keep, whether `High` is
better than `H`, which date a column holds. Another team could reasonably choose differently.
What matters is that the decisions are made deliberately, applied consistently, and recorded,
and SSM records every one of them in each standardised file's StandardisationLog.

A few choices are plain corrections, though: a replicate number like `FruitNumber` is a
**Number**, not a Measurement, and a column called `Height` isn't `Weight`. The tutorial
points these out as it goes.

## Sample files

| File | Used in |
| --- | --- |
| {download}`Dataset1.csv <../../_static/tutorial-data/Dataset1.csv>` | Chapter 1 |
| {download}`Dataset1_fixed.csv <../../_static/tutorial-data/Dataset1_fixed.csv>` | Chapters 1, 2 and 5 |
| {download}`Dataset2.xlsx <../../_static/tutorial-data/Dataset2.xlsx>` | Chapters 3 and 5 |

Expected results, to compare with your own:

| File | What it is |
| --- | --- |
| {download}`Fields.xlsx <../../_static/tutorial-data/Fields.xlsx>` | The finished Fields after chapter 4. Import it to skip straight to chapter 5. |
| {download}`Dataset1_fixed.std.xlsx <../../_static/tutorial-data/Dataset1_fixed.std.xlsx>` | Dataset1, standardised in chapter 5 |
| {download}`Dataset2_RawData.std.xlsx <../../_static/tutorial-data/Dataset2_RawData.std.xlsx>` | Dataset2, standardised in chapter 5 |
