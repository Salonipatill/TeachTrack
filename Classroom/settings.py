"""Local defaults with explicit production configuration. See docs/DEPLOYMENT.md."""
import os
import secrets
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in ('1', 'true', 'yes')
DEBUG = env_bool('DEBUG', True)
SECRET_KEY = os.getenv('SECRET_KEY', '')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('SECRET_KEY is required in production.')
    key_file = BASE_DIR / '.dev-secret'
    if not key_file.exists():
        try:
            with key_file.open('x') as f:
                f.write(secrets.token_urlsafe(64))
            key_file.chmod(0o600)
        except FileExistsError:
            pass
    SECRET_KEY = key_file.read_text().strip()
if not DEBUG and len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('Production SECRET_KEY must contain at least 50 characters.')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [h.strip() for h in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if h.strip()]
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
                  'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'ClassApp.apps.ClassAppConfig']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware',
              'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
              'ClassApp.middleware.RequestSizeLimitMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
              'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'Classroom.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'ClassApp' / 'Templates'], 'APP_DIRS': True,
              'OPTIONS': {'context_processors': ['django.template.context_processors.request',
              'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages',
              'ClassApp.context_processors.navigation']}}]
WSGI_APPLICATION = 'Classroom.wsgi.application'
DATABASES = {'default': dj_database_url.parse(os.getenv('DATABASE_URL') or f'sqlite:///{BASE_DIR / "db.sqlite3"}', conn_max_age=60, conn_health_checks=True)}
if DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
    DATABASES['default']['ENGINE'] = 'mysql.connector.django'
    DATABASES['default'].setdefault('OPTIONS', {}).update({
        'use_pure': True,
        'ssl_ca': str(BASE_DIR / 'certs' / 'aiven-ca.pem'),
        'ssl_verify_cert': True,
        'ssl_verify_identity': True,
    })
if not DEBUG and DATABASES['default']['ENGINE'] not in {'django.db.backends.postgresql', 'mysql.connector.django'}:
    raise ImproperlyConfigured('Production requires DATABASE_URL (PostgreSQL or MySQL).')
AUTH_PASSWORD_VALIDATORS = [
 {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
 {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'
STORAGES = {'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
            'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
UPLOADS_ENABLED = DEBUG or bool(os.getenv('GS_BUCKET_NAME'))
if not UPLOADS_ENABLED:
    STORAGES['default'] = {'BACKEND': 'ClassApp.storage.DisabledUploadStorage'}
if os.getenv('GS_BUCKET_NAME'):
    STORAGES['default'] = {'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage',
                          'OPTIONS': {'bucket_name': os.environ['GS_BUCKET_NAME'], 'default_acl': None, 'querystring_auth': True}}
# Media is streamed through an authenticated view; there is deliberately no public media route.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'
if env_bool('TRUST_PROXY_HEADERS'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FILES = 50
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'teachtrack@localhost')
LOGGING = {'version': 1, 'disable_existing_loggers': False,
           'handlers': {'console': {'class': 'logging.StreamHandler'}},
           'root': {'handlers': ['console'], 'level': 'INFO'}}
