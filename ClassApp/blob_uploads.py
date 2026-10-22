"""Authorize direct uploads and restore validated files for existing Django forms."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.urls import Resolver404, resolve
from django.views.decorators.http import require_POST

from .blob_storage import (BlobClient, BlobUnavailable, CONTENT_TYPES, MAX_FILE_SIZE,
                           VerifiedBlobFile, new_blob_path)

TICKET_SALT = 'teachtrack.private-blob-upload.v1'
TICKET_PREFIX = '_blob_'


def upload_target(user, path, field):
    if not user.is_authenticated or not user.is_active:
        raise PermissionDenied
    try:
        parsed = urlsplit(path)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError
        view = resolve(path).func.__name__
    except (Resolver404, ValueError, TypeError):
        raise PermissionDenied('Invalid upload destination.') from None
    role = user.profile.role
    allowed = {
        'resource_create': ('file', ('faculty', 'director')),
        'announcement_create': ('document', ('faculty', 'director')),
        'doubt_create': ('attachment', ('student',)),
        'quiz_create': (r'questions-(?:[0-9]|[1-4][0-9])-image', ('faculty', 'director')),
    }
    expected, roles = allowed.get(view, ('', ()))
    if role not in roles or not re.fullmatch(expected, field):
        raise PermissionDenied('Your role cannot upload a file here.')
    return view


@login_required
@require_POST
def upload_url(request):
    if settings.UPLOAD_STORAGE != 'blob':
        return JsonResponse({'error': 'Direct file storage is not configured.'}, status=503)
    try:
        data = json.loads(request.body)
        path, field, filename, size = (data[key] for key in ('path', 'field', 'filename', 'size'))
        if not all(isinstance(value, str) for value in (path, field, filename)):
            raise ValueError
        view = upload_target(request.user, path, field)
        if (not filename or len(filename) > 255 or Path(filename).name != filename or
                any(ord(c) < 32 or ord(c) == 127 for c in filename) or '\\' in filename):
            raise ValueError
        extension = Path(filename).suffix.lower()
        if extension not in CONTENT_TYPES or (view == 'quiz_create' and extension not in ('.jpg', '.jpeg', '.png')):
            return JsonResponse({'error': 'Choose a supported document, JPG or PNG file.'}, status=400)
        if type(size) is not int or not 0 < size <= MAX_FILE_SIZE:
            return JsonResponse({'error': 'Maximum file size is 30 MB; empty files are not supported.'}, status=400)
        pathname = new_blob_path(request.user.pk, filename)
        content_type = CONTENT_TYPES[extension]
        url = BlobClient().url(pathname, operation='put', content_type=content_type, maximum_size=size)
        ticket = signing.dumps({'user': request.user.pk, 'view': view, 'field': field,
                                'filename': filename, 'pathname': pathname, 'size': size,
                                'content_type': content_type}, salt=TICKET_SALT, compress=True)
    except (KeyError, TypeError, ValueError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid file details.'}, status=400)
    except BlobUnavailable:
        return JsonResponse({'error': 'File storage is temporarily unavailable. Please try again.'}, status=503)
    response = JsonResponse({'url': url, 'ticket': ticket, 'content_type': content_type})
    response['Cache-Control'] = 'private, no-store'
    return response


class DirectBlobUploadMiddleware:
    """Runs after CSRF and authentication, before the authorized form view."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method != 'POST':
            return None
        if settings.UPLOAD_STORAGE == 'blob' and request.FILES:
            return HttpResponse('Please enable JavaScript and use the direct file uploader.', status=400)
        tickets = [(name[len(TICKET_PREFIX):], request.POST.getlist(name))
                   for name in request.POST if name.startswith(TICKET_PREFIX)]
        if not tickets:
            return None
        if settings.UPLOAD_STORAGE != 'blob':
            return HttpResponse('Direct file storage is unavailable. Please choose your file again.', status=503)
        try:
            if len(tickets) > 50:
                raise ValueError
            verified = []
            for field, values in tickets:
                view = upload_target(request.user, request.path, field)
                if len(values) != 1 or field in request.FILES:
                    raise ValueError
                data = signing.loads(values[0], salt=TICKET_SALT, max_age=30*60)
                if data['user'] != request.user.pk or data['view'] != view or data['field'] != field:
                    raise PermissionDenied('This file belongs to a different upload.')
                verified.append((field, data))
            if sum(data['size'] for _, data in verified) > 32*1024*1024:
                return HttpResponse('Total attachments must be at most 32 MB per form.', status=413)
            for field, data in verified:
                content = BlobClient().read(data['pathname'], expected_size=data['size'])
                request.FILES[field] = VerifiedBlobFile(content=content, filename=data['filename'],
                                                       pathname=data['pathname'], content_type=data['content_type'])
        except (signing.BadSignature, KeyError, ValueError, TypeError):
            return HttpResponse('This upload has expired or is invalid. Please choose your file again.', status=400)
        except FileNotFoundError:
            return HttpResponse('The upload was not completed. Please choose your file again.', status=400)
        except BlobUnavailable:
            return HttpResponse('File storage is temporarily unavailable. Please try again.', status=503)
        return None
