from functools import wraps
from django.http import JsonResponse

from account.authentication import decode_access_token
from account.models import User


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('access_token')
        print(f"DEBUG: Access token from cookie: {token}")

        if not token:
            print("DEBUG: No access token found in cookies")
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            payload = decode_access_token(token)
            print(f"DEBUG: Token payload: {payload}")
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except Exception as e:
            print(f"DEBUG: Token decode error: {e}")
            return JsonResponse({'error': str(e)}, status=401)

        return view_func(request, *args, **kwargs)
    return wrapper




from django.http import HttpResponseForbidden

# def role_required(*allowed_roles):
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#             if request.user.role in allowed_roles:
#                 return view_func(request, *args, **kwargs)
#             return HttpResponseForbidden("You don't have permission to access this resource.")
#         return _wrapped_view
#     return decorator

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Option 1: Redirect to login page
                # return redirect('login_view')
                
                # Option 2 (alternate): Return a 403 response
                return HttpResponseForbidden("You must be logged in.")

            if hasattr(request.user, 'role') and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("You don't have permission to access this resource.")
        return _wrapped_view
    return decorator


