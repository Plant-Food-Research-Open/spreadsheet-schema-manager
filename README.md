# Spreadsheet Schema Manager

Spreadsheet Schema Manager is a web-based tool for standardising spreadsheet metadata and
improving data consistency across projects and teams. Built with [Rio](https://rio.dev/), it
helps streamline spreadsheet-based data collection workflows by centrally defining Fields,
auto-generating ready-to-fill Excel templates, and bootstrapping metadata standards from legacy
spreadsheets while standardising them at the same time.

![Spreadsheet Schema Manager overview](docs/SSM-Overview.png)

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

## Scope & Beta Feedback

Spreadsheet Schema Manager is currently in beta. The current version focuses on spreadsheets
that contain a single fixed-column table with simple headers. Support for variable column
structures or complex 2D matrix-style tables is not available at this stage.

## Tech stack

- [Rio](https://rio.dev/) — Python web app framework (UI and backend logic both live in Python)
- MongoDB — persistence
- MinIO / S3 — file storage
- Keycloak — SSO authentication (OpenID Connect)

## Getting started

### Prerequisites

- Python 3.12+
- A running MongoDB instance
- A running MinIO/S3-compatible object store

### Install

```bash
pip install -r requirements.txt
```

### Run locally

```bash
python -m rio run
```

Rio serves the app at `http://localhost:8000` by default (see `rio.toml`). For local development
without a Keycloak instance, set `AUTH_DISABLED=true` (see below) to bypass SSO entirely.

### Configuration

The app is configured entirely via environment variables:

| Variable | Purpose |
| --- | --- |
| `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` | MongoDB credentials |
| `MONGO_APP` / `MONGO_PORT` | MongoDB host / port |
| `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | MinIO/S3 credentials |
| `MINIO_URL` / `BUCKET_NAME` | MinIO/S3 endpoint and bucket |
| `AUTH_SECRET_KEY` / `AUTH_REDIRECT_URI` | Keycloak OAuth client secret and redirect URI |
| `AUTH_DISABLED` | When `true`, bypasses Keycloak login and attaches a fresh, isolated synthetic user to every session. **Only use this in local dev, UAT, or test environments — never in production.** |
| `TEST_USER_NAME` / `TEST_USER_EMAIL` | Display name/email used for the synthetic user when `AUTH_DISABLED=true` |

> **Note:** the Keycloak issuer URL is currently hardcoded in `auth.py`.
> Self-hosting this app against a different identity provider requires changing that.

## Deployment

Kubernetes manifests for the `dev`, `uat`, and `prod` environments live under `deployment/`,
deployed via ArgoCD. Notable jobs:

- `deployment/prod/backup-cronjob.yml` — nightly MongoDB backup to NFS storage.
- `deployment/uat/cleanup-cronjob.yml` — nightly UAT test-data wipe.
- `deployment/dev/restore-cronjob.yml` — manually-triggered dev database restore from the latest
  prod backup.

## Testing

- Unit tests: `tests/` (Python `unittest`-based).
- End-to-end tests: see the companion `spreadsheet-schema-manager-rio-playwright-tests`
  repository.

## License

Licensed under the Apache License, Version 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.
