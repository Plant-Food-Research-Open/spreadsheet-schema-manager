# Extra CA certificates

Any `*.crt` files placed in this directory before `docker build` are added to the
image's trusted CA bundle (and used for outbound HTTPS, e.g. to your identity
provider via `REQUESTS_CA_BUNDLE`).

Certificates are organisation-specific and must not be committed — `*.crt` here is
git-ignored. CI pipelines typically copy them in from a secret store before building.
