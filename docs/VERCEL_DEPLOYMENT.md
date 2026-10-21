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
dj-database-url is remapped to mysql.connector.django. TLS uses use_pure=True,
ssl_ca, ssl_verify_cert=True and ssl_verify_identity=True. The public certificate
at certs/aiven-ca.pem must match the service. The Git exception includes that CA
certificate only; private keys and passwords must remain excluded.

## Schema and startup

Run migrations through a trusted terminal configured for the intended database:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check --deploy
```

Migration 0010 adds batch and separate submission academic snapshots. Preserve
existing records and back up populated databases before upgrades. Migrations are
not run on every web request. See UPGRADE.md for original-schema migrations.

## Files and email

GS_BUCKET_NAME can be blank. In production, uploads then remain disabled and show
a clear message; do not rely on Vercel's local filesystem to preserve uploads.
To enable files, provision private GCS storage and its credentials first. Aiven
stores application records, not the uploaded file bodies. Supabase storage is
not integrated.

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
