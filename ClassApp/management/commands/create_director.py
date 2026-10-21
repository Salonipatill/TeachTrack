import getpass
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from ClassApp.models import Profile
class Command(BaseCommand):
    help = 'Create a director account. Password is entered privately and is never printed.'
    def add_arguments(self, parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--email', required=True)
        parser.add_argument('--name', default='Director')
    def handle(self, *args, **opts):
        if get_user_model().objects.filter(username=opts['username']).exists():
            raise CommandError('Username already exists. No changes made.')
        password = getpass.getpass('Director password: ')
        if password != getpass.getpass('Confirm password: '):
            raise CommandError('Passwords do not match.')
        user = get_user_model()(username=opts['username'],email=opts['email'],first_name=opts['name'])
        try:
            validate_password(password, user)
            user.full_clean(exclude=['password'])
        except ValidationError as e:
            raise CommandError('; '.join(e.messages))
        with transaction.atomic():
            user.set_password(password)
            user.save()
            Profile.objects.filter(user=user).update(role='director')
            from ClassApp.services import ensure_legacy
            ensure_legacy(user,'director')
        self.stdout.write(self.style.SUCCESS('Director account created. Sign in with the username you supplied.'))
