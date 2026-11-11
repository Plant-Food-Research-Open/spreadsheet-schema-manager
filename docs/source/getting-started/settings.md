# Settings

Open **Settings** from the navigation bar, change what you need, then select
**Save Settings**.

Preferred date format
: How dates are written when SSM standardises a Date column and when it fills date cells in
  a downloaded Workbook. Choose from `YYYY-MM-DD` (for example `2026-04-03`), `DD/MM/YYYY`
  (`03/04/2026`) or `DD-MMM-YYYY` (`03-Apr-2026`). The default, `YYYY-MM-DD`, is the
  international standard ISO 8601 date format. It can't be misread as month-first or
  day-first, so keep it unless you need another format.

Include constant Category fields in the raw data sheet of a downloaded Workbook
: A Category Field narrowed to a single value in a Workbook is a
  [constant Category Field](concepts.md#constant-category-fields). By default it's recorded
  once on the Workbook's `ConstantCategoryFields` sheet. Turn this on to also add it as a
  column on the data sheet, with the value repeated on every row. That's useful when the file
  will be merged with other data. The standardised output of a Dataset always includes these
  columns.

Current active team
: The space you work in: leave it empty for your personal space, or choose a team to work in
  its shared space. See [Who can see what](concepts.md#who-can-see-what). Only teams you've
  been added to are listed.
