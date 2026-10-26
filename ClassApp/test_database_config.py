"""Configuration checks do not require a MySQL server or real credentials."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from Classroom.database import database_config


class DatabaseConfigurationTests(SimpleTestCase):
    base_dir = Path(__file__).resolve().parent.parent

    def config(self, **env):
        return database_config(self.base_dir, {'DATABASE_URL': 'mysql://user:p%40ss@localhost:3306/app', **env})

    def test_default_preserves_aiven_certificate_and_hostname_verification(self):
        config = self.config()
        self.assertEqual(config['ENGINE'], 'mysql.connector.django')
        self.assertEqual(config['PASSWORD'], 'p@ss')
        self.assertEqual(config['OPTIONS']['ssl_ca'], str((self.base_dir / 'certs/aiven-ca.pem').resolve()))
        self.assertTrue(config['OPTIONS']['ssl_verify_cert'])
        self.assertTrue(config['OPTIONS']['ssl_verify_identity'])
        self.assertFalse(config['OPTIONS']['ssl_disabled'])

    def test_local_mysql_disables_ssl_without_loading_any_certificate(self):
        config = self.config(MYSQL_SSL_MODE='disabled', MYSQL_SSL_CA='does-not-exist.pem')
        self.assertTrue(config['OPTIONS']['ssl_disabled'])
        self.assertNotIn('ssl_ca', config['OPTIONS'])
        self.assertNotIn('ssl_verify_identity', config['OPTIONS'])

    def test_connector_url_uses_the_same_environment_configuration(self):
        config = self.config(DATABASE_URL='mysql-connector://user:pw@localhost/app', MYSQL_SSL_MODE='DISABLED')
        self.assertEqual(config['ENGINE'], 'mysql.connector.django')
        self.assertTrue(config['OPTIONS']['ssl_disabled'])

    def test_custom_ca_relative_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            ca = Path(tmp) / 'ca.pem'
            ca.write_text('test certificate placeholder')
            for path in ['ca.pem', str(ca)]:
                config = database_config(tmp, {'DATABASE_URL': 'mysql://u:p@server/app', 'MYSQL_SSL_CA': path, 'MYSQL_SSL_MODE': 'VERIFY_CA'})
                self.assertEqual(config['OPTIONS']['ssl_ca'], str(ca.resolve()))
                self.assertTrue(config['OPTIONS']['ssl_verify_cert'])
                self.assertFalse(config['OPTIONS']['ssl_verify_identity'])

    def test_client_certificate_and_key_are_paired(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'supplied together'):
            self.config(MYSQL_SSL_CERT='client.pem')
        with tempfile.TemporaryDirectory() as tmp:
            cert, key = Path(tmp) / 'client.pem', Path(tmp) / 'client.key'
            cert.touch()
            key.touch()
            config = self.config(MYSQL_SSL_CERT=str(cert), MYSQL_SSL_KEY=str(key))
            self.assertEqual(config['OPTIONS']['ssl_cert'], str(cert.resolve()))
            self.assertEqual(config['OPTIONS']['ssl_key'], str(key.resolve()))

    def test_invalid_ssl_modes_and_missing_ca_fail_clearly(self):
        with self.assertRaisesMessage(ImproperlyConfigured, 'MYSQL_SSL_MODE'):
            self.config(MYSQL_SSL_MODE='unknown')
        with self.assertRaisesMessage(ImproperlyConfigured, 'MYSQL_SSL_CA'):
            self.config(MYSQL_SSL_CA='missing.pem')

    def test_connection_lifetime_timeout_and_driver_are_configurable(self):
        config = self.config(MYSQL_CONNECT_TIMEOUT='7', MYSQL_USE_PURE='False', DATABASE_CONN_MAX_AGE='0', DATABASE_CONN_HEALTH_CHECKS='False')
        self.assertEqual(config['OPTIONS']['connection_timeout'], 7)
        self.assertFalse(config['OPTIONS']['use_pure'])
        self.assertEqual(config['CONN_MAX_AGE'], 0)
        self.assertFalse(config['CONN_HEALTH_CHECKS'])

    def test_invalid_numeric_and_boolean_options_fail_clearly(self):
        for name, value in [('MYSQL_CONNECT_TIMEOUT', '0'), ('MYSQL_CONNECT_TIMEOUT', 'abc'), ('MYSQL_USE_PURE', 'maybe'), ('DATABASE_CONN_MAX_AGE', '-1'), ('DATABASE_CONN_HEALTH_CHECKS', 'maybe')]:
            with self.subTest(name=name, value=value), self.assertRaisesMessage(ImproperlyConfigured, name):
                self.config(**{name: value})

    def test_environment_ssl_replaces_uri_ssl_options(self):
        config = self.config(DATABASE_URL='mysql://u:p@localhost/app?ssl_mode=VERIFY_IDENTITY&ssl_ca=wrong.pem', MYSQL_SSL_MODE='DISABLED')
        self.assertEqual({key for key in config['OPTIONS'] if key.startswith('ssl')}, {'ssl_disabled'})

    def test_sqlite_and_postgresql_ignore_mysql_settings(self):
        for url, engine in [('sqlite:///:memory:', 'django.db.backends.sqlite3'), ('postgresql://u:p@localhost/app', 'django.db.backends.postgresql')]:
            config = self.config(DATABASE_URL=url, MYSQL_SSL_MODE='invalid')
            self.assertEqual(config['ENGINE'], engine)
            self.assertNotIn('ssl_ca', config.get('OPTIONS', {}))

    def test_blank_url_keeps_sqlite_fallback(self):
        config = self.config(DATABASE_URL='')
        self.assertEqual(config['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(config['NAME'], str(self.base_dir / 'db.sqlite3'))

    def test_invalid_url_error_does_not_echo_credentials(self):
        with self.assertRaises(ImproperlyConfigured) as error:
            self.config(DATABASE_URL='unknown://u:secret-password@server/app')
        self.assertNotIn('secret-password', str(error.exception))

    def test_selected_private_environment_file_is_used_by_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / '.env.local-test'
            file.write_text('DATABASE_URL=mysql://u:p@127.0.0.1/local_test\nMYSQL_SSL_MODE=DISABLED\n')
            env = os.environ.copy()
            env.pop('DATABASE_URL', None)
            env.pop('MYSQL_SSL_MODE', None)
            env.update(TEACHTRACK_ENV_FILE=str(file), DEBUG='True')
            script = "from Classroom.settings import DATABASES; c=DATABASES['default']; assert c['NAME']=='local_test'; assert c['OPTIONS']['ssl_disabled']"
            result = subprocess.run([sys.executable, '-c', script], cwd=self.base_dir, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_runserver_loads_the_selected_file_over_inherited_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / '.env.local-test'
            file.write_text('DATABASE_URL=mysql://u:p@127.0.0.1/local_test\nMYSQL_SSL_MODE=DISABLED\n')
            env = os.environ.copy()
            env.update(TEACHTRACK_ENV_FILE=str(file), DEBUG='True', DATABASE_URL='sqlite:///:memory:', MYSQL_SSL_MODE='VERIFY_IDENTITY')
            script = """import sys
from unittest.mock import patch
import manage
def check(argv):
    from Classroom.settings import DATABASES
    assert DATABASES['default']['NAME'] == 'local_test'
    assert DATABASES['default']['OPTIONS']['ssl_disabled']
sys.argv = ['manage.py', 'runserver']
with patch('django.core.management.execute_from_command_line', check):
    manage.main()
"""
            result = subprocess.run([sys.executable, '-c', script], cwd=self.base_dir, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
