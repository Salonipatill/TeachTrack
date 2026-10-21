"""Storage used when production uploads have not been configured."""
from django.core.files.storage import Storage


class DisabledUploadStorage(Storage):
    def _save(self, name, content):
        raise OSError('File uploads are temporarily unavailable.')

    def _open(self, name, mode='rb'):
        raise FileNotFoundError('File storage is unavailable.')

    def exists(self, name):
        return False

    def url(self, name):
        return '#'
