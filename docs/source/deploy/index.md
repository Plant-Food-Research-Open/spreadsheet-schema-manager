# Deploy and operate

SSM runs as a Python web app backed by MongoDB, an S3-compatible object store (SeaweedFS) for
uploaded and generated files, and Keycloak for single sign-on.

```{toctree}
:maxdepth: 1

local-development
configuration
kubernetes
```

This repository holds only generic **templates** of the deployment files. Keep
organisation-specific values (registry, hostnames, storage classes, backup share, identity
provider, CI credential IDs) in a separate, private deployment repository.
