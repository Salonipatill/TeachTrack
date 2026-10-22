from django.http import HttpResponse
from django.conf import settings
class RequestSizeLimitMiddleware:
    """Reject known oversized requests before CSRF parsing or temporary file creation."""
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        try:
            size = int(request.META.get('CONTENT_LENGTH') or 0)
        except ValueError:
            return HttpResponse('Invalid Content-Length.', status=400)
        if size > 32 * 1024 * 1024:
            return HttpResponse('Request too large. Resource files must be at most 30 MB.', status=413)
        if not settings.UPLOADS_ENABLED and request.method in {'POST', 'PUT', 'PATCH'} and request.FILES:
            return HttpResponse('File uploads are temporarily unavailable. You can submit this form without a file if the attachment is optional.', status=503)
        response = self.get_response(request)
        if getattr(request, 'user', None) and request.user.is_authenticated:
            response['Cache-Control'] = 'private, no-store'
        return response
