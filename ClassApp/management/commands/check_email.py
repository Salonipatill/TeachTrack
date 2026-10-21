"""Verify SMTP configuration without displaying credentials."""
from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Check email configuration; optionally send a test to an address you provide.'

    def add_arguments(self, parser):
        parser.add_argument('--connect', action='store_true', help='Test SMTP login without sending email.')
        parser.add_argument('--send-to', help='Send one test email to this address.')

    def handle(self, *args, **options):
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
            raise CommandError('Email is not using SMTP. Set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend.')
        missing = [name for name in ('EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD')
                   if not getattr(settings, name)]
        if missing:
            raise CommandError('Missing settings: ' + ', '.join(missing) + '. See docs/EMAIL_SETUP.md.')
        if not (settings.EMAIL_USE_TLS or settings.EMAIL_USE_SSL):
            raise CommandError('Enable EMAIL_USE_TLS or EMAIL_USE_SSL for encrypted email delivery.')
        if not settings.DEFAULT_FROM_EMAIL or settings.DEFAULT_FROM_EMAIL.endswith('@localhost'):
            raise CommandError('Set DEFAULT_FROM_EMAIL to an email address accepted by your provider.')
        self.stdout.write(self.style.SUCCESS('SMTP settings are present. Credentials were not displayed.'))
        if options['connect'] or options['send_to']:
            try:
                with get_connection() as connection:
                    if options['send_to']:
                        send_mail('TeachTrack email test', 'Email delivery is configured for TeachTrack.',
                                  settings.DEFAULT_FROM_EMAIL, [options['send_to']], connection=connection)
            except Exception:
                raise CommandError('SMTP connection or delivery failed. Check provider credentials, TLS/SSL and network access.') from None
            self.stdout.write(self.style.SUCCESS('Test email accepted by SMTP.' if options['send_to'] else 'SMTP connection and login succeeded.'))
