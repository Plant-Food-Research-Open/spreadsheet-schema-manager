# Spreadsheet Schema Manager

Spreadsheet Schema Manager is a web-based tool for standardising spreadsheet metadata and
improving data consistency across projects and teams. Built with [Rio](https://rio.dev/), it
helps streamline spreadsheet-based data collection workflows by centrally defining Fields,
auto-generating ready-to-fill Excel templates, and bootstrapping metadata standards from legacy
spreadsheets while standardising them at the same time.

![Spreadsheet Schema Manager overview](docs/source/_static/ssm-overview.png)

## Features

- **Centrally define Fields** — reusable field (data column) definitions (Category, Measurement,
  Text, Number, Date) for consistency across projects and teams, with import/export to/from
  Excel.
- **Auto-generate Excel templates** — group Fields into a reusable **Template**, then instantiate
  a **Workbook** with pre-filled headers and data validation, ready for data collection (with an
  optional QR-code reference sheet).
- **Bootstrap and standardise legacy spreadsheets** — upload existing spreadsheet data as a
  **Dataset** and standardise it against a Field schema, bringing legacy data in line with your
  metadata standards.

## Documentation

Full documentation, including tutorials, configuration and deployment, is at
**https://spreadsheet-schema-manager.readthedocs.io**.

## Scope

The current version supports spreadsheets that contain a single fixed-column table with simple
headers. Variable column structures and complex 2D matrix-style tables are not supported.

## Quick start

Requires Python 3.12+, MongoDB and a SeaweedFS (S3-compatible) object store.

```bash
pip install -r requirements.txt
AUTH_DISABLED=true python -m rio run
```

`AUTH_DISABLED=true` skips Keycloak login for local development; never use it in production.
See [Configuration](https://spreadsheet-schema-manager.readthedocs.io/en/latest/deploy/configuration.html)
for the other environment variables, and
[Deploy and operate](https://spreadsheet-schema-manager.readthedocs.io/en/latest/deploy/index.html)
for the Helm chart and other deployment templates in this repo.

## Testing

- Unit tests: `python -m unittest discover -s tests`
- End-to-end tests (Playwright):
  [spreadsheet-schema-manager-tests](https://github.com/Plant-Food-Research-Open/spreadsheet-schema-manager-tests)

## Contributing

Contributions are welcome. If you are planning a change, please open an issue or discussion first
so the intended approach and scope are clear.

When updating application behaviour, configuration, or deployment wiring, also update the
documentation in `docs/source/` so the project remains easy to operate and understand.

## License

Licensed under the Apache License, Version 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

## Funding

Funded by the New Zealand Ministry of Business, Innovation and Employment Strategic Science
Investment Fund (contract number C11X1702) as part of the Digital Horticulture Systems Ngā Pou
Rangahau, a Growing Futures™ programme at The New Zealand Institute for Bioeconomy Science
Limited (Bioeconomy Science Institute).
