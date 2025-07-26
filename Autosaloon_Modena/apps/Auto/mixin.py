from django.http import HttpResponseForbidden

from apps.utils import is_possessore_auto


class UserIsOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not is_possessore_auto(request.user, obj):
            return HttpResponseForbidden("Non sei il possessore di questa auto.")
        return super().dispatch(request, *args, **kwargs)
