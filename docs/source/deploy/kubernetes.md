# Build and deploy to Kubernetes

## Container image

The `Dockerfile` builds the app image and runs it in release mode on port 8000.

To trust internal certificate authorities, for example for your identity provider, put their
`*.crt` files in `certs/` before building. They're added to the image's trusted CA bundle.
`*.crt` files there are git-ignored: CI pipelines usually copy them in from a secret store.

`builds/Jenkinsfile.template` is an example Jenkins pipeline that builds the image, runs the
unit tests inside it and pushes it to a registry.

## Helm chart

`deployment/helm/ssm` deploys the app together with MongoDB and an in-pod SeaweedFS S3 gateway,
exposes the app through an ingress, and provisions the persistent volumes and config maps.

`values.yaml` holds generic defaults. Override the values marked `REQUIRED` in your own
overlays:

- `image.repository`: where your CI pushes the image
- `ingress.host`: the app's public hostname
- `auth.issuer`: your Keycloak realm URL, unless `auth.disabled` is `true`
- `nfs.server` and `nfs.path` for each backup or restore job you enable

Secrets are created outside the chart and referenced by name:

| Value | Default name | Holds |
| --- | --- | --- |
| `secrets.db` | `db-secret` | `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` |
| `secrets.s3` | `s3-secret` | `S3_ACCESS_KEY`, `S3_SECRET_KEY` |
| `secrets.auth` | `auth-secret` | `AUTH_SECRET_KEY` |

Deploy with your overlays:

```bash
helm upgrade --install ssm ./deployment/helm/ssm \
  -f ../my-ssm-deploy/deployment/helm/ssm/values-common.yaml \
  -f ../my-ssm-deploy/deployment/helm/ssm/values-prod.yaml
```

With ArgoCD, use a multi-source Application: the chart from this repository and the values
files from your deployment repository through a `$values` reference.

## Scheduled jobs

All jobs are off by default.

| Value | What it does | Schedule |
| --- | --- | --- |
| `backup` | Backs up MongoDB to an NFS share | Daily |
| `restore` | Restores MongoDB from the latest backup | Manual only |
| `backupS3` | Copies the SeaweedFS bucket to the NFS share | Manual only |
| `restoreS3` | Restores the bucket from the latest copy | Manual only |
| `cleanup` | **Deletes all app data in MongoDB** | Daily |
| `cleanupS3` | **Deletes every file in the bucket** | Daily |

:::{danger}
`cleanup` and `cleanupS3` exist to reset test environments between test runs. Never enable
them in production.
:::
