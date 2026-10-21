"""Check a configured MySQL server and optionally run the isolated Django suite."""
from argparse import ArgumentParser
import os
import logging
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', default='.env', help='Private environment file, relative to the project root.')
    parser.add_argument('--run-tests', action='store_true', help='Create a unique test database, run the suite, then remove it.')
    parser.add_argument('--test-label', action='append', help='Optional Django test label for a focused rerun; default is all ClassApp tests.')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    from dotenv import dotenv_values
    file = Path(args.env_file)
    if not file.is_absolute():
        file = ROOT / file
    if not file.is_file():
        parser.error('The selected private environment file does not exist.')
    values = dotenv_values(file)
    if not values.get('DATABASE_URL'):
        parser.error('Set DATABASE_URL in the selected file. Credentials are never printed.')
    for name, value in values.items():
        if value is not None:
            os.environ[name] = value
    os.environ.update(DEBUG='True', DJANGO_SETTINGS_MODULE='Classroom.settings', TEACHTRACK_ENV_FILE=str(file.resolve()))
    import django
    django.setup()
    logging.getLogger('django.request').setLevel(logging.CRITICAL)
    logging.getLogger('mysql.connector').setLevel(logging.WARNING)
    from django.conf import settings
    from django.db import connection
    if connection.vendor != 'mysql':
        parser.error('The selected configuration must use MySQL.')
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT VERSION()')
            print('MySQL server version:', cursor.fetchone()[0], flush=True)
            cursor.execute("SHOW STATUS LIKE 'Ssl_cipher'")
            row = cursor.fetchone()
            encrypted = bool(row and row[1])
            print('TLS active:', encrypted, flush=True)
        if not settings.DATABASES['default']['OPTIONS'].get('ssl_disabled') and not encrypted:
            raise RuntimeError('Configured TLS connection is not encrypted.')
    except Exception:
        raise SystemExit('MySQL connection check failed. Check the private URL, server availability and SSL settings; credentials were not printed.') from None
    finally:
        connection.close()
    if args.run_tests:
        # Never reuse or destroy a fixed-name test database or the application database.
        test_name = 'test_teachtrack_' + uuid.uuid4().hex[:16]
        settings.DATABASES['default'].setdefault('TEST', {})['NAME'] = test_name
        print('Running isolated suite in', test_name, flush=True)
        from django.test.runner import DiscoverRunner
        failures = DiscoverRunner(verbosity=1, interactive=False, keepdb=False).run_tests(args.test_label or ['ClassApp'])
        raise SystemExit(bool(failures))


if __name__ == '__main__':
    main()
