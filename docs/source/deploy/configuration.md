# Configuration

The app is configured entirely through environment variables.

| Variable | Purpose |
| --- | --- |
| `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` | MongoDB credentials |
| `MONGO_APP` / `MONGO_PORT` | MongoDB host and port |
| `S3_ACCESS_KEY` / `S3_SECRET_KEY` | S3 credentials |
| `S3_URL` / `BUCKET_NAME` | S3 endpoint and bucket |
| `AUTH_ISSUER` | Keycloak realm URL, for example `https://keycloak.example.com/realms/<realm>`. Required unless `AUTH_DISABLED=true`. |
| `AUTH_CLIENT_ID` | Keycloak OAuth client ID (default `spreadsheet-schema`) |
| `AUTH_SECRET_KEY` / `AUTH_REDIRECT_URI` | Keycloak OAuth client secret and redirect URI |
| `AUTH_PROVIDER_LABEL` | Name on the login button, "Log in via _label_ SSO" (default `Keycloak`) |
| `AUTH_DISABLED` | When `true`, bypasses Keycloak and gives every session a fresh, isolated synthetic user. Never use in production. |
| `TEST_USER_NAME` / `TEST_USER_EMAIL` | Name and email of the synthetic user when `AUTH_DISABLED=true` |
| `REQUESTS_CA_BUNDLE` | CA bundle used for outbound HTTPS, such as to Keycloak |
