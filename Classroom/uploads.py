"""Choose upload storage independently of the database and debug mode."""
import os

from django.core.exceptions import ImproperlyConfigured


def upload_storage_config(debug, env=None):
    env = os.environ if env is None else env
    mode = (env.get('UPLOAD_STORAGE') or 'auto').strip().lower()
    bucket = (env.get('GS_BUCKET_NAME') or '').strip()
    blob_ready = bool((env.get('BLOB_READ_WRITE_TOKEN') or '').strip() or
                      ((env.get('BLOB_STORE_ID') or '').strip() and (env.get('VERCEL_OIDC_TOKEN') or '').strip()))
    if mode == 'auto':
        mode = 'blob' if blob_ready else ('gcs' if bucket else ('local' if debug else 'disabled'))
    if mode == 'blob':
        if not blob_ready:
            raise ImproperlyConfigured('UPLOAD_STORAGE=blob requires BLOB_READ_WRITE_TOKEN or BLOB_STORE_ID with VERCEL_OIDC_TOKEN.')
        return mode, {'BACKEND': 'ClassApp.blob_storage.PrivateBlobStorage'}
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
    raise ImproperlyConfigured('UPLOAD_STORAGE must be auto, local, blob, gcs or disabled.')
