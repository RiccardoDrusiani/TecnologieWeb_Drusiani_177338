from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseForbidden


class UtenteRequiredMixin(AccessMixin):
    """Permette l'accesso solo agli utenti del gruppo 'concessionaria'."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.groups.filter(name="utente").exists():
            return HttpResponseForbidden("Accesso riservato agli utenti.")
        return super().dispatch(request, *args, **kwargs)