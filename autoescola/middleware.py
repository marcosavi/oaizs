from django.utils.timezone import now #type: ignore
from django.contrib.auth import get_user_model #type: ignore

class UpdateLastLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        #padrao para cionfigurar e inicializar

    def __call__(self, request):
        #executado a cada request antes da view ser chamada
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            # Resolve the actual user model from the SimpleLazyObject
            User = get_user_model()
            # Make sure to only update the last_login for an actual user object
            if hasattr(request.user, 'id') and request.user.id is not None:
                User.objects.filter(pk=request.user.pk).update(last_login=now())
        
        return response


class StreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            today = now().date()
            user = request.user
            if user.last_login_date:
                if user.last_login_date == today:
                    # User already recorded today
                    return response
                elif (today - user.last_login_date).days == 1:
                    # User logged in consecutively
                    user.login_streak += 1
                else:
                    # Break in streak
                    user.login_streak = 1
            else:
                # First time login is being tracked
                user.login_streak = 1
            user.last_login_date = today
            user.save(update_fields=['last_login_date', 'login_streak'])
        return response