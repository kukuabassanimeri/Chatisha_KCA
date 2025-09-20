from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('chatisha_kca:login')  # must login first

            if request.user.role not in allowed_roles:
                return redirect('chatisha_kca:login')  # block access if wrong role

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
