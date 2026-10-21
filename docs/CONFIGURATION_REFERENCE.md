# TeachTrack configuration reference

This reference covers the environment variables read by Classroom/settings.py and the project’s custom management commands. Examples are placeholders. It intentionally does not reproduce the private .env file or live database/SMTP credentials.

## 1. Loading and precedence

settings.py calls load_dotenv(BASE_DIR / '.env') with the default non-overriding behavior. An existing process environment value wins over the .env entry. This includes values inherited from an IDE or parent shell. Editing .env may therefore have no effect until the conflicting process value is changed and the server is restarted.

Boolean settings treat the case-insensitive strings 1, true and yes as true. Other values, including release, are false. Lists such as ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS are comma-separated, stripped and filtered for empty entries. PORT belongs to the container startup command, not the Django settings parser.

## 2. Environment variable index

| Variable | Default / fallback | Meaning and use |
| --- | --- | --- |
| DEBUG | True when absent | Development flag; affects secret fallback, production guards, HTTPS/cookies and demo command availability |
| SECRET_KEY | Blank | Development reads or creates .dev-secret when blank; production requires an explicit value at least 50 characters long |
| ALLOWED_HOSTS | localhost,127.0.0.1,[::1] | Accepted request hostnames; entries have no URL scheme |
| CSRF_TRUSTED_ORIGINS | Empty list | Additional trusted origins including the exact scheme and host for production forms |
| DATABASE_URL | Blank | Blank selects sqlite:///BASE_DIR/db.sqlite3; otherwise parsed by dj-database-url |
| GS_BUCKET_NAME | Blank | Blank uses local FileSystemStorage; a value selects private GoogleCloudStorage |
| TRUST_PROXY_HEADERS | False | When true, uses HTTP_X_FORWARDED_PROTO=https to recognize a trusted proxy’s HTTPS scheme |
| EMAIL_BACKEND | django.core.mail.backends.console.EmailBackend | Development reset email is printed; use an SMTP backend for delivery |
| EMAIL_HOST | Empty | SMTP server hostname |
| EMAIL_PORT | 587 | Parsed as an integer; invalid numeric text prevents successful settings loading |
| EMAIL_HOST_USER | Empty | SMTP login username |
| EMAIL_HOST_PASSWORD | Empty | SMTP credential; keep private |
| EMAIL_USE_TLS | True | SMTP TLS setting parsed with the boolean helper |
| DEFAULT_FROM_EMAIL | teachtrack@localhost | Reset-email sender address/display value |
| DEMO_PASSWORD | Empty | seed_demo-only chosen password; validated before creating sample accounts |
| PORT | 8080 in Docker environment | Gunicorn bind port in the Docker shell command; normally supplied by Cloud Run at runtime |
| DJANGO_SETTINGS_MODULE | Classroom.settings in entry points | Django configuration module selected by manage.py/WSGI/ASGI; standard Django entry-point behavior |

### SECRET_KEY lifecycle

With DEBUG=True and no SECRET_KEY value, settings.py generates a random token_urlsafe(64) in .dev-secret if the file does not exist, then reads that persistent local value. Creation uses exclusive file mode to handle a concurrent first start. The code requests restrictive file permissions; platform behavior can differ. Do not delete or rotate this file as a routine startup step.

With DEBUG=False, an empty key raises ImproperlyConfigured. A non-empty key shorter than 50 characters also raises. The production value should be supplied through the target environment’s secret mechanism; the build-only Docker value is not the runtime key.

### Database URL shapes

| Engine | Illustrative shape | Dependency |
| --- | --- | --- |
| SQLite | sqlite:///C:/path/to/fresh.sqlite3 on Windows; sqlite:////absolute/path/fresh.sqlite3 on Linux | Python SQLite support |
| MySQL | mysql://USER:URL_ENCODED_PASSWORD@HOST:3306/DATABASE | requirements-mysql.txt |
| PostgreSQL | postgresql://USER:URL_ENCODED_PASSWORD@HOST:5432/DATABASE | Main psycopg dependency |
| Cloud SQL PostgreSQL socket | postgresql://USER:URL_ENCODED_PASSWORD@/DATABASE?host=/cloudsql/PROJECT:REGION:INSTANCE | Main psycopg dependency plus runtime connection permissions |

Use a URL-encoded credential value where required. A URL is configuration, not database provisioning. The selected server/database must already be reachable and the user must have the intended privileges. dj-database-url is called with conn_max_age=60 and conn_health_checks=True.

## 3. Production guards

| Condition | Startup result |
| --- | --- |
| DEBUG=False with no SECRET_KEY | Rejected |
| DEBUG=False with SECRET_KEY shorter than 50 characters | Rejected |
| DEBUG=False with an engine other than PostgreSQL/MySQL | Rejected |
| DEBUG=False without GS_BUCKET_NAME | Rejected |
| DEBUG=True with no database URL | Uses local db.sqlite3 path |
| DEBUG=True without a bucket | Uses local MEDIA_ROOT |

These explicit checks do not verify the server’s actual database connection, bucket permissions, SMTP delivery or DNS. Validate those separately after provisioning.

## 4. Fixed Django settings

These are code-level settings, not additional environment variables in this implementation. Setting an environment variable named SESSION_COOKIE_AGE, for example, does not override the hardcoded value unless settings.py is changed to read it.

| Setting | Value / behavior |
| --- | --- |
| INSTALLED_APPS | Django admin, auth, contenttypes, sessions, messages, staticfiles; ClassApp.apps.ClassAppConfig |
| ROOT_URLCONF | Classroom.urls |
| WSGI_APPLICATION | Classroom.wsgi.application |
| Template backend | DjangoTemplates; APP_DIRS=True; explicit ClassApp/Templates directory |
| Template context processors | request, auth, messages; custom navigation role/unread count |
| DEFAULT_AUTO_FIELD | django.db.models.BigAutoField |
| LANGUAGE_CODE | en-us |
| TIME_ZONE | Asia/Kolkata |
| USE_I18N / USE_TZ | True / True |
| LOGIN_URL | Named route login |
| LOGIN_REDIRECT_URL | Named route dashboard |
| LOGOUT_REDIRECT_URL | Named route login |
| SESSION_COOKIE_HTTPONLY | True |
| SESSION_COOKIE_SAMESITE | Lax |
| SESSION_COOKIE_AGE | 3600 seconds |
| SESSION_EXPIRE_AT_BROWSER_CLOSE | True |
| SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE | not DEBUG |
| SECURE_SSL_REDIRECT | not DEBUG |
| SECURE_HSTS_SECONDS | 31536000 in production; 0 in development |
| SECURE_HSTS_INCLUDE_SUBDOMAINS / PRELOAD | not DEBUG |
| SECURE_CONTENT_TYPE_NOSNIFF | True |
| X_FRAME_OPTIONS | DENY |
| SECURE_REFERRER_POLICY | same-origin |
| SECURE_PROXY_SSL_HEADER | HTTP_X_FORWARDED_PROTO=https only if TRUST_PROXY_HEADERS is true |
| Logging | Console handler, INFO root level, existing loggers not disabled |

### Storage settings

| Setting | Value |
| --- | --- |
| STATIC_URL | /static/ |
| STATIC_ROOT | BASE_DIR/staticfiles |
| MEDIA_ROOT | BASE_DIR/media |
| Default local storage | django.core.files.storage.FileSystemStorage |
| Static storage | whitenoise.storage.CompressedManifestStaticFilesStorage |
| Bucket storage | storages.backends.gcloud.GoogleCloudStorage |
| GCS options | bucket_name from GS_BUCKET_NAME; default_acl=None; querystring_auth=True |

MEDIA_ROOT does not create a public media route. Private views determine which authenticated user may receive a stored attachment. The build step creates the hashed static mapping used for cacheable presentation assets; user uploads are a different storage category.

### Input and password policy

| Setting/rule | Value |
| --- | --- |
| FILE_UPLOAD_MAX_MEMORY_SIZE | 1 MiB; larger uploads can use temporary file storage |
| DATA_UPLOAD_MAX_MEMORY_SIZE | 12 MiB for Django request-data handling |
| DATA_UPLOAD_MAX_NUMBER_FILES | 50 |
| Custom declared body limit | Greater than 12 MiB is rejected by middleware |
| Custom per-file limit | Greater than 10 MiB is rejected by validation |
| Office archive expanded limit | Must remain below 50 MiB |
| Password similarity validator | Django UserAttributeSimilarityValidator |
| Minimum password length | 10 |
| Common-password rejection | Django CommonPasswordValidator |
| Numeric-only rejection | Django NumericPasswordValidator |
| Pagination | 15 records per page in paginated helper |
| Question formset | 1–50 forms, deletion supported, questions prefix |
| Login throttle | 10 failures; stored window older than 15 minutes resets on next request |

## 5. Development example

Use .env.example as a starting point for a new environment. Keep an existing working .env instead of overwriting it.

```dotenv
DEBUG=True
SECRET_KEY=
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
GS_BUCKET_NAME=
TRUST_PROXY_HEADERS=False
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=teachtrack@localhost
```

The empty database URL selects the project SQLite path, so verify whether a database file already exists there. For this project’s original incomplete historical SQLite database, follow the fresh/legacy guidance in the handbook rather than forcing migrations.

## 6. Production configuration example

The following shows variable names and placeholder shapes, not ready-to-use credentials. Replace the hostname, private bucket, database and SMTP values with provisioned configuration.

```dotenv
DEBUG=False
SECRET_KEY=REPLACE_WITH_A_PRIVATE_RANDOM_VALUE_OF_AT_LEAST_50_CHARACTERS
ALLOWED_HOSTS=YOUR_SERVICE_HOST
CSRF_TRUSTED_ORIGINS=https://YOUR_SERVICE_HOST
DATABASE_URL=postgresql://USER:URL_ENCODED_PASSWORD@HOST:5432/DATABASE
GS_BUCKET_NAME=YOUR_PRIVATE_BUCKET
TRUST_PROXY_HEADERS=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=YOUR_SMTP_HOST
EMAIL_PORT=587
EMAIL_HOST_USER=YOUR_SMTP_USERNAME
EMAIL_HOST_PASSWORD=YOUR_PRIVATE_SMTP_CREDENTIAL
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=TeachTrack <YOUR_VERIFIED_SENDER>
```

Enable TRUST_PROXY_HEADERS only when the actual deployment replaces and controls that forwarding header. A direct untrusted client must not be able to assert its own HTTPS scheme. The Docker image uses a Linux Gunicorn process; the Windows runserver command remains a development entry point.

## 7. Runtime and operator checks

The Dockerfile also sets PYTHONDONTWRITEBYTECODE=1 to avoid writing Python bytecode files in the container and PYTHONUNBUFFERED=1 to send Python output without standard stream buffering. Its default PORT is 8080. These are container/Python process settings, separate from the Django environment parser above.

Use manage.py check to validate Django configuration, showmigrations to inspect the selected database’s schema state, and the isolated test procedure in the handbook for automated validation. /health/ checks the process only; it does not establish database/bucket/SMTP readiness.

Changing an environment value requires restarting the relevant application process. When a localhost page remains stale, inspect whether an older server process still serves the same port. Do not solve configuration confusion by printing the entire private environment or deleting the configured database.
