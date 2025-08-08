import datetime
from functools import wraps

from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from apps.Utente.models import UserModelBan
from apps.Auto.models import Commento

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

def ban_check(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                ban_profile = request.user.user_ban_profile
                now = timezone.now()
                if ban_profile.data_fine_ban and now < ban_profile.data_fine_ban:
                    remaining = ban_profile.data_fine_ban - now
                    minutes = int(remaining.total_seconds() // 60)
                    messages.error(request, f"Sei bannato! Tempo rimanente: {minutes} minuti.")
                    return redirect('Utente:login')
            except UserModelBan.DoesNotExist:
                pass
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def user_is_banned(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Recupera l'utente da segnalare (se presente)
        commento_id = request.POST.get('commento_id') or request.GET.get('commento_id')
        if commento_id:
            try:
                commento = Commento.objects.get(id=commento_id)
                segnalato = commento.user
                ban_profile, _ = UserModelBan.objects.get_or_create(user=segnalato)
                ban_profile.segnalazioni = (ban_profile.segnalazioni or 0)
                if ban_profile.segnalazioni >= 4:
                    now = timezone.now()
                    ban_hours = 2 * (2 ** (ban_profile.qnt_ban or 0))
                    ban_profile.data_inizio_ban = now
                    ban_profile.data_fine_ban = now + timezone.timedelta(hours=ban_hours)
                    ban_profile.qnt_ban = (ban_profile.qnt_ban or 0) + 1
                    ban_profile.segnalazioni = 0
                ban_profile.save()
            except Commento.DoesNotExist:
                pass
        return view_func(request, *args, **kwargs)
    return _wrapped_view
