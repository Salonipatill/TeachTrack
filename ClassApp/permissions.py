from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def roles(*allowed):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.profile.role not in allowed:
                raise PermissionDenied('Your role cannot access this page.')
            return view(request, *args, **kwargs)
        return wrapped
    return decorator
