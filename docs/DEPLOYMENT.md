# Google Cloud Run deployment

> Email password reset and SMTP delivery have been removed. Only signed-in password changes are available; EMAIL_* environment variables are no longer used.


This is a deployment guide and container configuration, not evidence of an already deployed service. You need your own Google Cloud project, billing, gcloud CLI and permission to create resources. Use your actual project, region, service account and hostname. Review cloud costs before creating services.

The intended deployment uses Cloud Run for Django, Cloud SQL PostgreSQL for records, a private Cloud Storage bucket for resources, Secret Manager for credentials and WhiteNoise for collected static files.

Official references:
- https://docs.cloud.google.com/python/django/run
- https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- https://django-storages.readthedocs.io/en/latest/backends/gcloud.html

## Existing original media and database

The main guide below uses PostgreSQL. To retain an original MySQL installation, optional requirements-mysql.txt is supplied for a separate staging upgrade; translating between database engines is not performed automatically by Django migrations. Rehearse the real database separately as described in UPGRADE.md.

The ZIP retains the original media directory. Before enabling private cloud storage for an existing installation, copy those objects into the private bucket under the same relative paths (for example attachments/, announcements/ and quiz_images/). Do not make the bucket public. Validate both old attachment paths and new uploads after the copy.

## 1. Provision infrastructure

In Google Cloud Console:

1. Select your project. Enable Cloud Run, Cloud Build, Artifact Registry, Cloud SQL Admin, Secret Manager and Cloud Storage APIs.
2. Create a regional Artifact Registry Docker repository named teachtrack.
3. Create a Cloud SQL PostgreSQL instance with backups, a database named teachtrack and a dedicated application database user. Copy the instance connection name `PROJECT:REGION:INSTANCE`.
4. Create a private Cloud Storage bucket with uniform bucket-level access and public access prevention. Do not grant allUsers access.
5. Create a dedicated application service account. Give it Cloud SQL Client, Secret Manager Secret Accessor on only the required secrets and Storage Object User on only the private bucket. Use Google-managed workload identity, not downloaded credential JSON.

## 2. Create secrets

Store these in Secret Manager:

- `teachtrack-secret-key`: a random value from `python -c "import secrets; print(secrets.token_urlsafe(64))"`.
- `teachtrack-database-url`: `postgresql://USER:URL_ENCODED_PASSWORD@/teachtrack?host=/cloudsql/PROJECT:REGION:INSTANCE`.

Grant the application service account access to those individual secrets. Never put production values in the source folder or Docker image.

## 3. Build and publish the image

The following examples use bash in Cloud Shell. Replace every placeholder before running.

```bash
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT/teachtrack/app:release-1 .
```

Run from the TeachTrack folder. The Dockerfile installs pinned dependencies and collects static files during build. It runs Gunicorn as a non-root user. Migrations are deliberately separate from web startup to avoid races between instances.

## 4. Prepare runtime configuration

Create an untracked `cloudrun.env.yaml` outside your source control. Replace the example values. Find/reserve your intended Cloud Run URL or custom HTTPS hostname before enabling production requests; use that exact host for CSRF/ALLOWED_HOSTS. No wildcard host is needed.

```yaml
DEBUG: "False"
ALLOWED_HOSTS: "YOUR_SERVICE_HOST.run.app"
CSRF_TRUSTED_ORIGINS: "https://YOUR_SERVICE_HOST.run.app"
GS_BUCKET_NAME: "YOUR_PRIVATE_BUCKET"
TRUST_PROXY_HEADERS: "True"
```

Cloud Run supplies PORT automatically. Do not set it manually. The app relies on the trusted Cloud Run proxy to replace HTTPS forwarding headers. Do not enable TRUST_PROXY_HEADERS on an untrusted direct internet server.

## 5. Run a migration job

```bash
gcloud run jobs create teachtrack-migrate \
  --image REGION-docker.pkg.dev/PROJECT/teachtrack/app:release-1 \
  --region REGION \
  --service-account APP_SERVICE_ACCOUNT_EMAIL \
  --set-cloudsql-instances PROJECT:REGION:INSTANCE \
  --env-vars-file cloudrun.env.yaml \
  --set-secrets SECRET_KEY=teachtrack-secret-key:latest,DATABASE_URL=teachtrack-database-url:latest \
  --command python --args manage.py,migrate,--noinput

gcloud run jobs execute teachtrack-migrate --region REGION --wait
```

On later releases, update the job image and execute it before switching traffic. Use a Cloud SQL Auth Proxy connection from a trusted local terminal to run the interactive `create_director` command against the new production database. Configure DATABASE_URL for that proxy and the production environment, using environment variables rather than source changes. If working from a machine without bucket access, no media is read by create_director, but production settings still require the bucket name.

Do not create initial accounts using the local demo command in production. Keep the legacy student import optional and run it only against a backed-up database with reviewed source data.

## 6. Deploy the web service

```bash
gcloud run deploy teachtrack \
  --image REGION-docker.pkg.dev/PROJECT/teachtrack/app:release-1 \
  --region REGION \
  --service-account APP_SERVICE_ACCOUNT_EMAIL \
  --add-cloudsql-instances PROJECT:REGION:INSTANCE \
  --env-vars-file cloudrun.env.yaml \
  --set-secrets SECRET_KEY=teachtrack-secret-key:latest,DATABASE_URL=teachtrack-database-url:latest \
  --allow-unauthenticated \
  --port 8080 \
  --max-instances 3
```

`--allow-unauthenticated` exposes the Django login page; protected application pages still require Django authentication. If your organization requires Cloud Run IAM access as well, omit this flag and arrange access accordingly. Apply a separate ingress/load-balancer request-size policy suitable for 10 MB files, including requests without Content-Length. The middleware rejects declared request bodies above 12 MB; file validation rejects files above 10 MB after upload parsing. Test this policy with your actual ingress setup.

## 7. Validate before submission

- Run `python manage.py check --deploy` with the production environment and test database connectivity.
- Open /health/ (simple process health, not a database readiness check).
- Open the login page; inspect a /static/ClassApp/app.css request.
- Test all three roles, account deactivation, CSRF forms and logout.
- Upload a resource to the private bucket and download it through the authenticated app.
- Confirm the raw bucket object is inaccessible anonymously.
- Submit a quiz, answer a doubt, resolve a complaint and export CSV reports.
- Verify Cloud SQL backups and object retention policies.
- Test response times/concurrent submissions at your intended classroom size.

Local SQLite and local media are intentionally rejected when DEBUG=False; Cloud Run's writable filesystem is not durable. Logs go to stdout/stderr. Never log passwords, cookies or full credentials. Keep secrets and dependencies updated and review release/security advisories before deployment.
