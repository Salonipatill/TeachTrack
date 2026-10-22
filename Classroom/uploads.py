"""Choose upload storage independently of the database and debug mode."""
import os

from django.core.exceptions import ImproperlyConfigured


def upload_storage_config(debug, env=None):
    env = os.environ if env is None else env
    mode = (env.get('UPLOAD_STORAGE') or 'auto').strip().lower()
    bucket = (env.get('GS_BUCKET_NAME') or '').strip()
    if mode == 'auto':
        mode = 'gcs' if bucket else ('local' if debug else 'disabled')
    if mode == 'local':
        return mode, {'BACKEND': 'django.core.files.storage.FileSystemStorage'}
    if mode == 'gcs':
        if not bucket:
            raise ImproperlyConfigured('UPLOAD_STORAGE=gcs requires GS_BUCKET_NAME.')
        return mode, {
            'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage',
            'OPTIONS': {'bucket_name': bucket, 'default_acl': None, 'querystring_auth': True},
        }
    if mode == 'disabled':
        return mode, {'BACKEND': 'ClassApp.storage.DisabledUploadStorage'}
    raise ImproperlyConfigured('UPLOAD_STORAGE must be auto, local, gcs or disabled.')
