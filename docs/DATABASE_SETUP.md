# Local MySQL and Aiven configuration

Both use `mysql.connector.django`. No source-code edit is needed when changing
environments. Existing Aiven deployments retain certificate and hostname
verification by default. Changing databases does not copy or synchronize data.

## Personal PC

Create an actual MySQL database and user on your PC. In a private ignored file
such as `.env.local-mysql`, set:

```dotenv
DEBUG=True
DATABASE_URL=mysql://USER:URL_ENCODED_PASSWORD@127.0.0.1:3306/teachtrack
MYSQL_SSL_MODE=DISABLED
MYSQL_CONNECT_TIMEOUT=10
UPLOAD_STORAGE=local
GS_BUCKET_NAME=
```

Use SSL disabled only for trusted local development. It skips all CA/client-key
paths and sets Connector's ssl_disabled=True; a local MySQL installation does
not need to trust the unrelated Aiven certificate.

Select the private file from the TeachTrack folder:

```powershell
$env:TEACHTRACK_ENV_FILE = '.env.local-mysql'
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

CMD equivalent: `set TEACHTRACK_ENV_FILE=.env.local-mysql`. Close the terminal or
remove the selector to return to `.env`. Management commands give existing process
variables precedence; local runserver deliberately loads the selected file with
override=True. Avoid stale DATABASE_URL/MYSQL_* variables in the shell.

Migrate creates the schema in the selected database; it does not import Aiven
accounts or quiz records. Restore a reviewed backup if you need the same data.
Keep `.env.local-mysql` and credentials out of Git.

Notes and attachments upload directly to `TeachTrack/media/` in local mode.
Google Cloud and its credentials are not required. MySQL stores file paths and
resource details; back up the media directory along with the database. Faculty
and directors can upload notes from **Resource library → Upload a resource**;
signed-in students can download them through TeachTrack.

## Aiven on Vercel

Configure Vercel environment values independently of your PC:

```dotenv
DEBUG=False
DATABASE_URL=mysql://USER:URL_ENCODED_PASSWORD@AIVEN_HOST:PORT/DATABASE
MYSQL_SSL_MODE=VERIFY_IDENTITY
MYSQL_SSL_CA=certs/aiven-ca.pem
MYSQL_USE_PURE=True
MYSQL_CONNECT_TIMEOUT=10
DATABASE_CONN_MAX_AGE=60
DATABASE_CONN_HEALTH_CHECKS=True
```

Keep the existing private SECRET_KEY, host and other deployment configuration.
Do not upload your local env file. The committed public CA must match the service.
Vercel cannot reach MySQL on your PC through localhost/127.0.0.1; those names
refer to the Vercel instance there. See [Vercel guide](VERCEL_DEPLOYMENT.md).

## SSL and connection options

| Variable | Default | Meaning |
| --- | --- | --- |
| MYSQL_SSL_MODE | VERIFY_IDENTITY | DISABLED, VERIFY_CA or VERIFY_IDENTITY; invalid modes fail clearly |
| MYSQL_SSL_CA | certs/aiven-ca.pem | CA file for verification modes; absolute or project-relative path |
| MYSQL_SSL_CERT / MYSQL_SSL_KEY | Blank | Optional paired client certificate/private key for mutual TLS |
| MYSQL_USE_PURE | True | Connector pure-Python implementation |
| MYSQL_CONNECT_TIMEOUT | 10 | Positive connection timeout in seconds |
| DATABASE_CONN_MAX_AGE | 60 | Connection reuse lifetime; 0 closes after each request |
| DATABASE_CONN_HEALTH_CHECKS | True | Check reused connections |
| TEACHTRACK_ENV_FILE | .env | Private config file, relative to the project root or absolute |

VERIFY_CA validates the chain without hostname checking. VERIFY_IDENTITY checks
both and is the preferred Aiven mode. Verified modes require an existing CA file.
Optional client certificate/key paths must be provided together. A certificate
file's existence is checked at startup; actual TLS validation happens at connect.

Environment SSL options override URI SSL query parameters. Put SSL configuration
in the variables above instead of mysqlclient-style `ssl_mode` URI parameters.
MySQL-only options do not alter SQLite/PostgreSQL behavior. `mysql://` and
`mysql-connector://` URIs receive the same Connector configuration.

## Read-only connectivity and isolated suite

```powershell
.\.venv\Scripts\python.exe tools/verify_mysql.py --env-file .env.local-mysql
.\.venv\Scripts\python.exe tools/verify_mysql.py --env-file .env
```

These commands connect, read the server version and check whether TLS is active;
they do not modify application records. The env file must contain DATABASE_URL.
To verify all current features on each server, explicitly allow a temporary test
database by adding `--run-tests`:

```powershell
.\.venv\Scripts\python.exe tools/verify_mysql.py --env-file .env.local-mysql --run-tests
.\.venv\Scripts\python.exe tools/verify_mysql.py --env-file .env --run-tests
```

The runner creates a random `test_teachtrack_...` database, applies migrations,
runs the complete ClassApp suite and removes that test database. The account needs
CREATE/DROP DATABASE permission. Existing application databases are not replaced.
Do not point manual migrations at production unintentionally. Interrupted test
runs may need cleanup of their printed, uniquely named test database.

The original-schema migration regression uses its own temporary SQLite subprocess;
the main MySQL suite exercises current schema migrations and feature workflows on
the selected MySQL server. A local connection URI and server access are required
to claim that live local-MySQL feature tests passed.

If local credentials are unavailable, tools/verify_local_mysql.py can instead
start a disposable MySQL instance from an installed server executable. It uses a
new temporary data directory and separate loopback port, not the existing service
or its accounts. See tools/README.md. This proves local engine compatibility but
does not verify a still-unconfigured application's local username/password.

## Verification record for this change

- SQLite: all 71 tests passed. The rating/configuration checks were rerun after
  the portable exception expectation was corrected; all 15 focused checks passed.
- Disposable local MySQL 8.0.46: TLS inactive as explicitly configured; all 71
  tests passed. Its unique test database and owned server were removed/stopped.
- Aiven MySQL 8.4.11: TLS active with the default certificate/hostname verification.
  The first 69-test run exposed two test portability expectations (Windows short
  versus resolved paths, and Connector's CHECK-constraint exception type). Both
  were corrected. All 15 final focused checks passed on Aiven, including every
  failed check and the final environment/configuration cases. Together the runs
  verified all 57 existing workflow tests and 14 final configuration checks;
  a redundant second complete cloud run was not performed.
- Production Django checks, static collection, dependency checks, Python compilation
  and documentation link checks passed.

Tests used unique disposable databases. Existing application databases were not
migrated or modified. The original-schema migration regression remains isolated
on SQLite. The user's existing PC MySQL username/password is not verified while
.env.local-mysql has no real DATABASE_URL; the separate disposable instance proves
local server compatibility. These checks do not certify all possible user inputs,
cloud storage permissions or the currently deployed Vercel version.
