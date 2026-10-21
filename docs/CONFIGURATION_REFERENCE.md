# Configuration reference

Updated 21 October 2026. Values below are placeholders, not live credentials.

## Loading and precedence

Classroom/settings.py loads .env without overriding process variables. WSGI,
ASGI and management commands therefore use the process environment first.
The deliberate exception is local manage.py runserver: it loads the project's
.env with override=True before Django starts. Do not use that behavior to infer
Vercel values; configure Vercel environment variables separately.

Booleans accept 1, true and yes, case-insensitively. Other strings, including
release, are false. Comma-separated host/origin lists are trimmed.

## Environment variable index

| Variable | Default / use |
| --- | --- |
| DEBUG | True locally, false when VERCEL is present; set False explicitly in production |
| SECRET_KEY | Locally reads/creates .dev-secret if blank; production requires at least 50 characters |
| DATABASE_URL | Blank selects local SQLite; otherwise dj-database-url parses the URI |
| ALLOWED_HOSTS | localhost,127.0.0.1,[::1]; add explicit custom production domains without schemes |
| CSRF_TRUSTED_ORIGINS | Explicit additional origins, including https:// |
| VERCEL | Presence changes DEBUG's fallback to false |
| VERCEL_URL | Provided deployment hostname; appended to host and HTTPS origin lists |
| VERCEL_PROJECT_PRODUCTION_URL | Provided production hostname; appended to host/origin lists |
| VERCEL_BRANCH_URL | Provided branch hostname; appended to host/origin lists |
| GS_BUCKET_NAME | Optional private Google Cloud Storage bucket; see upload modes below |
| TRUST_PROXY_HEADERS | False; True accepts HTTP_X_FORWARDED_PROTO=https from a trusted proxy |
| DEMO_PASSWORD | Explicit chosen password for development seed_demo; never a default production password |
| PORT | Container bind port, default 8080; not read by the Django settings parser |
| DJANGO_SETTINGS_MODULE | Classroom.settings in standard entry points |

EMAIL_* and DEFAULT_FROM_EMAIL environment variables are no longer read.
Outbound email uses django.core.mail.backends.dummy.EmailBackend. Public reset
links, email/phone OTP and SMTP setup are removed. Signed-in password change remains.

## Database backends

| Backend | URI shape | Behavior |
| --- | --- | --- |
| SQLite | sqlite:///PATH | Local development/test fallback |
| PostgreSQL | postgresql://USER:PASSWORD@HOST:PORT/DATABASE | psycopg from main requirements |
| MySQL / Aiven | mysql://USER:URL_ENCODED_PASSWORD@HOST:PORT/DATABASE | mysql-connector-python from main requirements |

MySQL configuration maps django.db.backends.mysql to mysql.connector.django.
OPTIONS contains use_pure=True, ssl_ca pointing at certs/aiven-ca.pem,
ssl_verify_cert=True and ssl_verify_identity=True. The public CA is committed;
private credentials and other private PEM/key files remain excluded. Use a
certificate matching the service and an existing database/user.

Connections use conn_max_age=60 and conn_health_checks=True. This is configuration,
not a connection or schema-readiness test. Never copy an unencoded password into
an example URI when it contains reserved URL characters.

## Upload modes

| Mode | Default storage | Uploads |
| --- | --- | --- |
| DEBUG=True, no bucket | Local MEDIA_ROOT | Enabled for development |
| GS_BUCKET_NAME configured | Private GCS backend | Enabled; runtime credentials/permissions still required |
| DEBUG=False, no bucket | ClassApp.storage.DisabledUploadStorage | Disabled |

UPLOADS_ENABLED is derived from DEBUG or the bucket name. The form explains the
unavailable state, middleware rejects file-bearing mutation requests, and the
storage backend refuses writes. Text-only workflows remain available. A bucket
is not required for production startup. Supabase is not implemented.

## Fixed settings and limits

- Production requires a nonempty SECRET_KEY of at least 50 characters and either
  PostgreSQL or mysql.connector.django. SQLite is rejected in production.
- TIME_ZONE=Asia/Kolkata; USE_TZ=True. Quiz launch/deadline and submission times
  are shown in IST. A batch is descriptive text, not a timetable assignment.
- STORAGES.staticfiles uses CompressedManifestStaticFilesStorage; run collectstatic
  for production, including theme.js, theme.css and favicon.svg.
- Session age is 3600 seconds; browser-close expiry, HTTP-only cookies and
  SameSite=Lax are configured. DEBUG=False enables secure cookies, HTTPS
  redirect and HSTS. Only trust forwarded HTTPS headers behind a trusted proxy.
- Password validation requires at least 10 characters plus Django's similarity,
  common-password and numeric-password checks.
- Files are limited to 10 MB by form validation; declared request bodies above
  12 MB are rejected. File content/image validation and private download
  authorization remain in place when storage is configured.
- Lists use 15 records per page. Quiz builders allow 1-50 questions. Login failure
  thresholds are 10 attempts per 15-minute username/peer-IP window.

## Examples

Development .env should be private. Copy .env.example and fill actual values.
For isolated checks, use a separate terminal with DEBUG=True and
DATABASE_URL=sqlite:///:memory:; close that terminal before normal database work.
See [Vercel deployment](VERCEL_DEPLOYMENT.md) for the current Aiven/Vercel example
and [Google Cloud guide](DEPLOYMENT.md) for the optional container/GCS deployment.

`manage.py check` validates Django configuration. `check --deploy` evaluates
production settings. Neither proves live database access, schema status, storage
permissions, deployed commit identity or DNS health. /health/ checks the process,
not database readiness. Secrets belong in private .env or platform secret storage.
