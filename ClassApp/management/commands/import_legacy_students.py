"""Read the uploaded legacy schema without modifying its database or migration history."""
import sqlite3
from contextlib import closing
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.db import transaction
from ClassApp.models import Profile
class Command(BaseCommand):
    help = 'Dry-run legacy ClassApp_student import. Add --apply to create hashed-password student accounts.'
    def add_arguments(self, parser):
        parser.add_argument('source')
        parser.add_argument('--apply', action='store_true')
    def handle(self, *args, **opts):
        path = Path(opts['source']).resolve()
        if not path.is_file():
            raise CommandError('Source SQLite database not found.')
        from django.conf import settings
        target = settings.DATABASES['default'].get('NAME')
        if target and str(path) == str(Path(str(target)).resolve()):
            raise CommandError('Source must be separate from the new TeachTrack database.')
        try:
            with closing(sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)) as source:
                source.row_factory = sqlite3.Row
                rows = source.execute('SELECT id,sname,sen,semail,unm,pw FROM ClassApp_student ORDER BY id').fetchall()
        except sqlite3.Error as e:
            raise CommandError('Source does not contain the supported legacy ClassApp_student schema.') from e
        User = get_user_model()
        seen = set()
        prepared = []
        for row in rows:
            username = row['unm'].strip()
            if username in seen or User.objects.filter(username=username).exists():
                raise CommandError(f'Conflicting username at legacy row {row["id"]}. No accounts imported. Resolve the conflict first.')
            seen.add(username)
            user = User(username=username,first_name=row['sname'],email=row['semail'])
            try:
                user.full_clean(exclude=['password'])
            except ValidationError as e:
                raise CommandError(f'Invalid legacy row {row["id"]}: {"; ".join(e.messages)}. No accounts imported.')
            prepared.append((user,row))
        if not opts['apply']:
            self.stdout.write(f'Dry run: {len(prepared)} student accounts eligible. Source unchanged. Add --apply to import.')
            return
        with transaction.atomic():
            for user,row in prepared:
                password = row['pw']
                if not password:
                    user.set_unusable_password()
                else:
                    try:
                        identify_hasher(password)
                    except ValueError:
                        user.set_password(password)
                    else:
                        user.password = password
                user.save()
                Profile.objects.filter(user=user).update(role='student', enrollment=row['sen'])
                from ClassApp.services import ensure_legacy
                record=ensure_legacy(user,'student');record.sen=row['sen'];record.save(update_fields=['sen'])
        self.stdout.write(self.style.SUCCESS(f'Imported {len(prepared)} students. Passwords are hashed. Source unchanged.'))
