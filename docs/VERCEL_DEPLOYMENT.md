# Vercel and Aiven deployment

Deploy the latest intended Git commit; retrying an older deployment can continue
to serve old templates and assets. Inspect the commit on the active deployment,
then use that deployment's Visit URL. A successful GitHub push alone does not
prove which version a browser is viewing.

## Environment

Configure these in Vercel for every environment that should run the application:

```dotenv
DEBUG=False
SECRET_KEY=YOUR_PRIVATE_RANDOM_KEY_AT_LEAST_50_CHARACTERS
DATABASE_URL=mysql://USER:URL_ENCODED_PASSWORD@YOUR_AIVEN_HOST:PORT/DATABASE
MYSQL_SSL_MODE=VERIFY_IDENTITY
MYSQL_SSL_CA=certs/aiven-ca.pem
UPLOAD_STORAGE=auto
ALLOWED_HOSTS=YOUR_CUSTOM_OR_STABLE_HOSTNAME
CSRF_TRUSTED_ORIGINS=https://YOUR_CUSTOM_OR_STABLE_HOSTNAME
```

Use the actual Aiven database name and credentials. Copy only each value into
Vercel's value field, without the KEY= prefix or quotes. Local .env files are
ignored by Git and are not transferred to Vercel. VERCEL_URL,
VERCEL_PROJECT_PRODUCTION_URL and VERCEL_BRANCH_URL are recognized automatically
when provided, accepting those exact hosts and HTTPS origins. DEBUG defaults off
when VERCEL is present; explicitly set it false for deployment.

The main requirements include mysql-connector-python. The MySQL engine parsed by
dj-database-url is remapped to mysql.connector.django. Default TLS uses MYSQL_SSL_MODE=VERIFY_IDENTITY and use_pure=True,
ssl_ca, ssl_verify_cert=True and ssl_verify_identity=True. The public certificate
at certs/aiven-ca.pem must match the service. The Git exception includes that CA
certificate only; private keys and passwords must remain excluded. Local MySQL can instead use MYSQL_SSL_MODE=DISABLED in a private development env file. See DATABASE_SETUP.md; no source change is needed.

## Schema and startup

Run migrations through a trusted terminal configured for the intended database:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check --deploy
```

Migration 0010 adds batch and separate submission academic snapshots. Preserve
existing records and back up populated databases before upgrades. Migration 0011
expands resource categories to 100 characters for custom category names. Migrations are
not run on every web request. See UPGRADE.md for original-schema migrations.

## Files and email

For Vercel uploads without Google Cloud, connect a **private Vercel Blob store**:

1. Open TeachTrack in Vercel, then **Storage > Create Storage > Blob**.
2. Choose **Private** access and connect it to TeachTrack for the intended environments.
3. Confirm Vercel added `BLOB_READ_WRITE_TOKEN`, or the platform-provided
   `BLOB_STORE_ID` and `VERCEL_OIDC_TOKEN`. Keep credentials in Vercel; never expose
   them in frontend variables or paste them into source/chat.
4. Set `UPLOAD_STORAGE=blob` and redeploy the commit containing this integration.
   `auto` also selects Blob when its credentials are present. Leave `GS_BUCKET_NAME` blank.
5. Sign in as faculty/director, upload a PNG and a 30 MB text/PDF resource, then
   download each as an authorized student. Check a quiz image, announcement
   document and student doubt attachment, including unauthorized access denial.

The browser sends bytes directly to private Blob using an exact-path, size/type
constrained, expiring PUT URL. A CSRF-protected endpoint checks role and destination
first. Django re-reads the bytes, checks the recorded size, and runs existing
document/Pillow validators before saving metadata. Signed form receipts are bound
to user, form and field, expiring after 30 minutes. Upload URLs expire after 15
minutes; read URLs after 5 minutes. Overwrites are disabled. Downloads and quiz
images apply existing access rules before redirecting to private signed GET URLs.
Long-lived tokens/signing keys never reach the browser. Blob needs no new migration;
stored paths use `blob/USER_ID/UUID/FILENAME`.

Each file may be up to 30 MiB; combined direct attachments are limited to 32 MiB per
form. Form submissions contain receipts and text, not binary files. JavaScript is
required. Failed uploads restore the button and selected file for retry. Invalid
or abandoned forms can leave unreferenced private blobs; review these in storage
before deleting them. Stored filenames are sanitized/truncated to fit legacy
100-character FileFields; resource metadata keeps the full original filename.

See [Vercel Signed URLs](https://vercel.com/docs/vercel-blob/vercel-signed-urls).
The official Python SDK does not expose this API yet, so the small Python adapter
follows the official JS protocol. Offline contract fixtures are generated with
`@vercel/blob@2.8.2`; see the tools README for regeneration.

Without Blob credentials or a GCS bucket, `auto` with `DEBUG=False` keeps uploads
disabled. Explicit `gcs` remains available with a private bucket and credentials.
`local` is for the PC or a server with persistent disk, independently of database.
After migration 0012, resources uploaded locally also keep a private ResourceFile
copy in the selected database. A Vercel instance using that same database can
download those resources even with uploads disabled and no local file. Existing
local resources require `preserve_resource_files --resource-id ID --apply` on
the machine that holds the file. A missing file without a saved database copy
still cannot be downloaded. Deploy the updated view after applying the migration.
This fallback covers resource-library files, not every legacy attachment.
Supabase storage is not integrated.

Vercel limits function request/response payloads to 4.5 MB. Blob mode bypasses these
limits for file bytes using direct transfers. The old database fallback still
returns bytes through a Function; legacy resources above that response limit need
moving to Blob. Smaller preserved resources still work after switching storage.
See [Vercel's function limits](https://vercel.com/docs/functions/limitations).

Public password reset, email/SMS OTP and SMTP sending are removed. EMAIL_*
variables are unused and can be removed from Vercel. If an App Password was
created solely for this retired feature, revoke it in the provider account.
Signed-in users can change passwords through the Password link.

## Post-deployment checks

1. Confirm the intended commit is Ready and open its Visit URL.
2. Verify the homepage, Contact header/footer, login and mobile navigation.
3. Verify the bottom-right theme toggle and saved choice after navigation.
4. Check that theme.js, theme.css, favicon.svg and application CSS return actual
   assets, not HTML login/error pages. Production asset filenames can be hashed.
5. Sign in as each role. Test director faculty creation, own profile edits and
   the student quiz form/result layout with an appropriate test account.
6. Read the actual failing request's runtime traceback if a 500 occurs; a
   successful homepage request does not establish database-backed flows work.

Deployment protection can redirect an independent visitor to Vercel login.
That redirect prevents unauthenticated live inspection; inspect the permitted
deployment in your account or provide an intentionally public production URL.
