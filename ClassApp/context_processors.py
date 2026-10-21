def navigation(request):
    if not request.user.is_authenticated:
        return {}
    return {'role': request.user.profile.role,
            'unread_count': request.user.notifications.filter(read_at__isnull=True).count()}
