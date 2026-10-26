def navigation(request):
    from django.conf import settings
    upload_context = {'uploads_enabled': settings.UPLOADS_ENABLED,
                      'direct_blob_uploads': settings.UPLOAD_STORAGE == 'blob'}
    if not request.user.is_authenticated:
        return upload_context
    return {'role': request.user.profile.role,
            **upload_context,
            'unread_count': request.user.notifications.filter(read_at__isnull=True).count()}
