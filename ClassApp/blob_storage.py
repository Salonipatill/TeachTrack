"""Private Blob storage and the small Vercel Signed URLs wire protocol.

The official Python SDK does not expose Signed URLs yet. This adapter follows
@vercel/blob 2.8.2's signed-token.ts and presign-query-params.ts (Apache-2.0):
https://github.com/vercel/storage/tree/main/packages/blob/src
Keep protocol fixtures in test_blob_storage.py in sync when upgrading it.
"""
import base64
import hashlib
import hmac
import json
import os
import re
import time
import uuid
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.core.files.uploadedfile import UploadedFile

MAX_FILE_SIZE = 30 * 1024 * 1024
CONTENT_TYPES = {
    '.pdf': 'application/pdf', '.txt': 'text/plain',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
}
API_URL = 'https://vercel.com/api/blob'
PATH_PATTERN = re.compile(r'blob/\d+/[a-f0-9]{32}/[^/\\\x00-\x1f\x7f]+\Z')


class BlobUnavailable(OSError):
    pass


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def is_blob_path(name):
    return bool(PATH_PATTERN.fullmatch(str(name)))


def new_blob_path(user_id, filename):
    # Keep paths below Django's legacy FileField max_length=100, preserving a
    # readable download filename. Resource.original_name retains the full name.
    stem = re.sub(r'[^\w. -]', '_', Path(filename).stem)[:35].strip(' .') or 'file'
    return f'blob/{user_id}/{uuid.uuid4().hex}/{stem}{Path(filename).suffix.lower()}'


def _b64url(value):
    return base64.urlsafe_b64encode(value).decode().rstrip('=')


def sign_url(material, pathname, operation, *, content_type=None, maximum_size=None):
    """Sign one exact path/operation; never return signing keys to the browser."""
    try:
        encoded = material['delegationToken'].split('.')[0]
        scope = json.loads(base64.urlsafe_b64decode(encoded + '=' * (-len(encoded) % 4)))
        store = scope['storeId'].removeprefix('store_')
        if (not re.fullmatch(r'[A-Za-z0-9]+', store) or scope['pathname'] != pathname or
                operation not in scope['operations'] or scope['validUntil'] <= int(time.time() * 1000)):
            raise ValueError
        params = {}
        if operation == 'put':
            params = {
                'vercel-blob-add-random-suffix': 'false',
                'vercel-blob-allow-overwrite': 'false',
                'vercel-blob-allowed-content-types': content_type,
                'vercel-blob-maximum-size-in-bytes': str(maximum_size),
            }
        elif operation not in ('get', 'head'):
            raise ValueError
        canonical = '\n'.join(sorted([f'operation={operation}', f'pathname={pathname}'] +
                                     [f'{key}={value}' for key, value in params.items()]))
        signature = _b64url(hmac.new(material['clientSigningToken'].encode(), canonical.encode(), hashlib.sha256).digest())
        params['vercel-blob-delegation'] = material['delegationToken']
        params['vercel-blob-signature'] = signature
        if operation == 'put':
            base = API_URL + '/?'+urlencode({'pathname': pathname})+'&'
        else:
            base = f'https://{store}.private.blob.vercel-storage.com/{quote(pathname, safe="/")}?'
        return base + urlencode(params)
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise BlobUnavailable('File storage returned an invalid signing response.') from error


class BlobClient:
    def __init__(self):
        self.opener = build_opener(NoRedirects())

    def _auth_headers(self):
        store = os.getenv('BLOB_STORE_ID', '').strip().removeprefix('store_')
        oidc = os.getenv('VERCEL_OIDC_TOKEN', '').strip()
        token = os.getenv('BLOB_READ_WRITE_TOKEN', '').strip()
        if oidc and store:
            bearer = oidc
        elif token:
            match = re.fullmatch(r'vercel_blob_rw_([A-Za-z0-9]+)_.+', token)
            if not match:
                raise BlobUnavailable('Vercel Blob credentials are invalid.')
            store, bearer = match[1], token
        else:
            raise BlobUnavailable('Vercel Blob is not connected.')
        if not re.fullmatch(r'[A-Za-z0-9]+', store):
            raise BlobUnavailable('Vercel Blob store id is invalid.')
        return {'Authorization': f'Bearer {bearer}', 'x-vercel-blob-store-id': store,
                'x-api-version': '13', 'Content-Type': 'application/json'}

    def _open_request(self, url, *, method='GET', data=None, headers=None):
        try:
            return self.opener.open(Request(url, data=data, method=method, headers=headers or {}), timeout=45)
        except HTTPError as error:
            if error.code == 404:
                raise FileNotFoundError('This file is unavailable.') from None
            raise BlobUnavailable('File storage is temporarily unavailable. Please try again.') from None
        except (URLError, TimeoutError, OSError):
            raise BlobUnavailable('File storage is temporarily unavailable. Please try again.') from None

    def url(self, pathname, *, operation='get', content_type=None, maximum_size=None):
        if not is_blob_path(pathname):
            raise FileNotFoundError('This file is unavailable.')
        payload = {'pathname': pathname, 'operations': [operation],
                   'validUntil': int(time.time() * 1000) + (15 if operation == 'put' else 5) * 60 * 1000}
        if operation == 'put':
            payload.update(allowedContentTypes=[content_type], maximumSizeInBytes=maximum_size)
        with self._open_request(API_URL+'/signed-token', method='POST',
                                data=json.dumps(payload).encode(), headers=self._auth_headers()) as response:
            try:
                material = json.loads(response.read(65536))
            except (ValueError, UnicodeDecodeError):
                raise BlobUnavailable('File storage returned an invalid response.') from None
        return sign_url(material, pathname, operation, content_type=content_type, maximum_size=maximum_size)

    def read(self, pathname, *, expected_size=None):
        if not is_blob_path(pathname):
            raise FileNotFoundError('This file is unavailable.')
        url = self.url(pathname)
        try:
            with self._open_request(url) as response:
                content = response.read(MAX_FILE_SIZE + 1)
        except FileNotFoundError:
            raise
        except OSError:
            raise BlobUnavailable('File storage is temporarily unavailable. Please try again.') from None
        if len(content) > MAX_FILE_SIZE or (expected_size is not None and len(content) != expected_size):
            raise BlobUnavailable('The uploaded file size does not match. Please choose the file again.')
        return content


class VerifiedBlobFile(UploadedFile):
    """Bytes re-read from the exact immutable blob bound to a signed form ticket."""
    def __init__(self, *, content, filename, pathname, content_type):
        super().__init__(BytesIO(content), name=filename, size=len(content), content_type=content_type)
        self.blob_pathname = pathname


class PrivateBlobStorage(Storage):
    def save(self, name, content, max_length=None):
        if isinstance(content, VerifiedBlobFile) and is_blob_path(content.blob_pathname):
            if max_length and len(content.blob_pathname) > max_length:
                raise BlobUnavailable('The file name is too long.')
            return content.blob_pathname
        # Interactive forms must use the direct uploader. Reject accidental
        # server-side uploads rather than send large bodies through Functions.
        raise BlobUnavailable('Please use the direct file uploader to upload this file.')

    def _open(self, name, mode='rb'):
        if mode != 'rb':
            raise ValueError('Blob files are read-only.')
        return ContentFile(BlobClient().read(name), name=name)

    def exists(self, name):
        if not is_blob_path(name):
            return False
        try:
            with BlobClient()._open_request(BlobClient().url(name, operation='head'), method='HEAD'):
                return True
        except FileNotFoundError:
            return False

    def url(self, name):
        return BlobClient().url(name)
