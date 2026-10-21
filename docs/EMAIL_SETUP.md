# Password-reset email setup

Students, faculty and directors share Django's email reset-link flow. SMS OTP is
not implemented. The recipient must have an active account with the entered email
address and a usable password. Unknown addresses receive the same confirmation
page to protect account privacy.

## Gmail SMTP

Enable Google 2-Step Verification, then create an App Password for TeachTrack:
https://support.google.com/accounts/answer/185833

Use the App Password, not the normal Google account password. Keep it private.
Some managed Google accounts do not allow App Passwords; use an approved SMTP
provider in that case.

Put these values in the ignored local `.env` and separately in Vercel's environment
variables for each deployed environment that needs password resets:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=YOUR_SENDING_GMAIL_ADDRESS
EMAIL_HOST_PASSWORD=YOUR_GOOGLE_APP_PASSWORD
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_TIMEOUT=10
DEFAULT_FROM_EMAIL=YOUR_SENDING_GMAIL_ADDRESS
```

Replace the uppercase placeholders. Do not commit credentials. In Vercel, paste
each value without the `KEY=` prefix or surrounding quotes, then deploy the latest
commit again. Local `.env` changes do not configure Vercel.

Other providers can use the same settings with their SMTP host, port, login and
approved sender. For implicit TLS on port 465 set `EMAIL_USE_SSL=True` and
`EMAIL_USE_TLS=False`. Never enable both modes.

## Verify

From the TeachTrack folder, with the virtual environment activated:

```cmd
set DEBUG=True
python manage.py check_email
python manage.py check_email --connect
```

The first command checks configuration only. The second tests SMTP login without
sending a message. To explicitly send a single test email to your own mailbox:

```cmd
python manage.py check_email --send-to YOUR_TEST_EMAIL_ADDRESS
```

Then request a reset from `/accounts/password/reset/` or any role's Forgot password
page using the account's stored email. Check spam. Open the emailed link and set a
new password. Login uses the account's username and the new password.

If a reset request produces no delivered email, check the backend is SMTP rather
than console, SMTP authentication/network access, the registered account email,
spam and provider delivery logs. Never enable public DEBUG to inspect email errors.

Django SMTP reference: https://docs.djangoproject.com/en/5.2/topics/email/
