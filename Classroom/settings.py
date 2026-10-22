"""Local defaults with explicit production configuration. See docs/DEPLOYMENT.md."""
import os
import secrets
from pathlib import Path
from .database import database_config
from .uploads import upload_storage_config
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = Path(os.getenv('TEACHTRACK_ENV_FILE') or '.env')
if not ENV_FILE.is_absolute():
    ENV_FILE = BASE_DIR / ENV_FILE
load_dotenv(ENV_FILE)
def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in ('1', 'true', 'yes')
DEBUG = env_bool('DEBUG', not bool(os.getenv('VERCEL')))
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
for vercel_url_variable in ('VERCEL_URL', 'VERCEL_PROJECT_PRODUCTION_URL', 'VERCEL_BRANCH_URL'):
    vercel_host = os.getenv(vercel_url_variable, '').strip()
    if vercel_host and '://' not in vercel_host and '/' not in vercel_host:
        if vercel_host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(vercel_host)
        vercel_origin = f'https://{vercel_host}'
        if vercel_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(vercel_origin)
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
DATABASES = {'default': database_config(BASE_DIR)}
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
UPLOAD_STORAGE, upload_backend = upload_storage_config(DEBUG)
STORAGES = {'default': upload_backend,
            'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
UPLOADS_ENABLED = UPLOAD_STORAGE != 'disabled'
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
DATA_UPLOAD_MAX_MEMORY_SIZE = 32 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FILES = 50
# Outbound email and public password reset are disabled.
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
LOGGING = {'version': 1, 'disable_existing_loggers': False,
           'handlers': {'console': {'class': 'logging.StreamHandler'}},
           'root': {'handlers': ['console'], 'level': 'INFO'}}
