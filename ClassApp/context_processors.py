def navigation(request):
    from django.conf import settings
    if not request.user.is_authenticated:
        return {'uploads_enabled': settings.UPLOADS_ENABLED}
    return {'role': request.user.profile.role,
            'uploads_enabled': settings.UPLOADS_ENABLED,
            'unread_count': request.user.notifications.filter(read_at__isnull=True).count()}
