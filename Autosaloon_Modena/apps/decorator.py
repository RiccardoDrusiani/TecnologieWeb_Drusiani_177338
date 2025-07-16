from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def user_or_concessionaria_required(func):
    """
    Decorator to check if the user is either authenticated as a concessionaria or a regular user.
    If not, it redirects to the login page or returns a 403 Forbidden error.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Reindirizza alla pagina di login
        if not hasattr(request.user, 'concessionaria') and not hasattr(request.user, 'is_user'):
            return HttpResponseForbidden("Accesso negato: non sei autorizzato a svolgere questa azione.")
        return func(request, *args, **kwargs)

    return wrapper
