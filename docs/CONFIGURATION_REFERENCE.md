# Configuration reference

Updated 22 October 2026. Values below are placeholders, not live credentials.

## Loading and precedence

Classroom/settings.py loads the file selected by TEACHTRACK_ENV_FILE (default .env) without overriding process variables. WSGI,
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
| TEACHTRACK_ENV_FILE | Private env-file path, relative to the project root or absolute; defaults to .env |
| MYSQL_SSL_MODE | VERIFY_IDENTITY by default; DISABLED for trusted local development, or VERIFY_CA |
| MYSQL_SSL_CA | CA path; default certs/aiven-ca.pem for verification modes; ignored when SSL is disabled |
| MYSQL_SSL_CERT / MYSQL_SSL_KEY | Optional paired client certificate/key paths for mutual TLS |
| MYSQL_USE_PURE | True; choose the Connector pure-Python implementation |
| MYSQL_CONNECT_TIMEOUT | Positive seconds, default 10 |
| DATABASE_CONN_MAX_AGE | Connection lifetime in seconds, default 60; zero closes after each request |
| DATABASE_CONN_HEALTH_CHECKS | True; reusable connection health checks |
| DATABASE_URL | Blank selects local SQLite; otherwise dj-database-url parses the URI |
| ALLOWED_HOSTS | localhost,127.0.0.1,[::1]; add explicit custom production domains without schemes |
| CSRF_TRUSTED_ORIGINS | Explicit additional origins, including https:// |
| VERCEL | Presence changes DEBUG's fallback to false |
| VERCEL_URL | Provided deployment hostname; appended to host and HTTPS origin lists |
| VERCEL_PROJECT_PRODUCTION_URL | Provided production hostname; appended to host/origin lists |
| VERCEL_BRANCH_URL | Provided branch hostname; appended to host/origin lists |
| GS_BUCKET_NAME | Optional private Google Cloud Storage bucket; see upload modes below |
| UPLOAD_STORAGE | auto (default), local, gcs or disabled; independent of the database engine |
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
Default OPTIONS preserve Aiven verification. MYSQL_SSL_MODE=DISABLED omits certificate options and sets ssl_disabled=True. VERIFY_CA checks the CA chain; VERIFY_IDENTITY also checks the hostname. Paths resolve from the project root, or may be absolute. See DATABASE_SETUP.md for complete examples. The public CA is committed;
private credentials and other private PEM/key files remain excluded. Use a
certificate matching the service and an existing database/user.

Connections use conn_max_age=60 and conn_health_checks=True. This is configuration,
not a connection or schema-readiness test. Never copy an unencoded password into
an example URI when it contains reserved URL characters.

## Upload modes

| Mode | Default storage | Uploads |
| --- | --- | --- |
| UPLOAD_STORAGE=local | Local MEDIA_ROOT (`media/`) | Enabled, including with DEBUG=False; no cloud credentials needed |
| UPLOAD_STORAGE=gcs | Private GCS backend | Enabled; GS_BUCKET_NAME and runtime credentials/permissions required |
| UPLOAD_STORAGE=disabled | ClassApp.storage.DisabledUploadStorage | Disabled |
| UPLOAD_STORAGE=auto (or unset) | GCS if a bucket exists, otherwise local when DEBUG=True, otherwise disabled | Preserves existing defaults |

UPLOADS_ENABLED is derived from the selected storage mode. With local storage,
MySQL stores resource details and file paths; file contents stay in MEDIA_ROOT.
Back up both the database and media directory. Use local mode on your PC or a
server with persistent disk; ephemeral hosting needs persistent external storage.
When storage is disabled, forms explain the unavailable state, middleware rejects
file-bearing mutation requests, and the storage backend refuses writes.
Text-only workflows remain available. A bucket
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
- Files are limited to 30 MB by form validation; declared request bodies above
  32 MB are rejected. File content/image validation and private download
  authorization remain in place when storage is configured.
- Resource uploads accept PDF, UTF-8 TXT, DOCX, PPTX, JPG, JPEG and PNG. A filename
  extension alone is insufficient: document content and image integrity are checked.
  FILE_UPLOAD_MAX_MEMORY_SIZE is 1 MB: it controls when uploads spill to temporary
  disk, not the allowed file size. DATA_UPLOAD_MAX_MEMORY_SIZE is 32 MB and at
  most 50 files can be parsed per request; the middleware's 32 MB total cap still
  applies to a multipart request containing several attachments.
- Resource custom category names allow up to 100 characters. Migration 0011
  expands the indexed category column; existing notes/pyq/assignment values remain.
- Lists use 15 records per page. Quiz builders allow 1-50 questions, with 2-26
  options per question and at least one correct answer. Login failure
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
