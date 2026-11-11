# Run locally

## Prerequisites

- Python 3.12 or later
- A running MongoDB instance
- A running SeaweedFS or other S3-compatible object store

## Install and run

```bash
pip install -r requirements.txt
python -m rio run
```

Rio serves the app at `http://localhost:8000` by default (see `rio.toml`). Set the
[environment variables](configuration.md) for MongoDB and S3 first.

To work without a Keycloak instance, set `AUTH_DISABLED=true`. Every session then gets a fresh,
isolated synthetic user instead of an SSO login.

:::{danger}
Only use `AUTH_DISABLED=true` for local development, UAT or test environments, never in
production.
:::
