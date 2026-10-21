"""Database configuration shared by local development and hosted deployments."""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured


def _boolean(env, name, default):
    value = str(env.get(name, '')).strip().lower()
    if not value:
        return default
    if value in {'1', 'true', 'yes'}:
        return True
    if value in {'0', 'false', 'no'}:
        return False
    raise ImproperlyConfigured(f'{name} must be True or False.')


def _integer(env, name, default, minimum=0):
    try:
        value = int(env.get(name) or default)
    except (TypeError, ValueError):
        raise ImproperlyConfigured(f'{name} must be an integer.') from None
    if value < minimum:
        raise ImproperlyConfigured(f'{name} must be at least {minimum}.')
    return value


def _certificate(base_dir, value, name):
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path(base_dir) / path
    if not path.is_file():
        raise ImproperlyConfigured(f'{name} must point to an existing certificate/key file.')
    return str(path.resolve())


def database_config(base_dir, env=None):
    env = os.environ if env is None else env
    url = (env.get('DATABASE_URL') or '').strip() or f'sqlite:///{Path(base_dir) / "db.sqlite3"}'
    try:
        config = dj_database_url.parse(
            url,
            conn_max_age=_integer(env, 'DATABASE_CONN_MAX_AGE', 60),
            conn_health_checks=_boolean(env, 'DATABASE_CONN_HEALTH_CHECKS', True),
        )
    except (ValueError, TypeError):
        raise ImproperlyConfigured('DATABASE_URL must be a valid database URI with URL-encoded credentials.') from None
    if config['ENGINE'] not in {'django.db.backends.mysql', 'mysql.connector.django'}:
        return config

    config['ENGINE'] = 'mysql.connector.django'
    options = config.setdefault('OPTIONS', {})
    options.pop('connect_timeout', None)
    # Environment SSL settings are authoritative, including when the URI has old
    # mysqlclient-style options. Do not send these to MySQL Connector/Python.
    for key in tuple(options):
        if key == 'ssl' or key.startswith('ssl_') or key.startswith('ssl-'):
            options.pop(key)
    options.update(
        use_pure=_boolean(env, 'MYSQL_USE_PURE', True),
        connection_timeout=_integer(env, 'MYSQL_CONNECT_TIMEOUT', 10, minimum=1),
    )
    mode = (env.get('MYSQL_SSL_MODE') or 'VERIFY_IDENTITY').strip().upper()
    if mode not in {'DISABLED', 'VERIFY_CA', 'VERIFY_IDENTITY'}:
        raise ImproperlyConfigured('MYSQL_SSL_MODE must be DISABLED, VERIFY_CA or VERIFY_IDENTITY.')
    if mode == 'DISABLED':
        options['ssl_disabled'] = True
        return config

    ca = (env.get('MYSQL_SSL_CA') or '').strip() or 'certs/aiven-ca.pem'
    options.update(
        ssl_disabled=False,
        ssl_ca=_certificate(base_dir, ca, 'MYSQL_SSL_CA'),
        ssl_verify_cert=True,
        ssl_verify_identity=mode == 'VERIFY_IDENTITY',
    )
    cert = (env.get('MYSQL_SSL_CERT') or '').strip()
    key = (env.get('MYSQL_SSL_KEY') or '').strip()
    if bool(cert) != bool(key):
        raise ImproperlyConfigured('MYSQL_SSL_CERT and MYSQL_SSL_KEY must be supplied together.')
    if cert:
        options['ssl_cert'] = _certificate(base_dir, cert, 'MYSQL_SSL_CERT')
        options['ssl_key'] = _certificate(base_dir, key, 'MYSQL_SSL_KEY')
    return config
