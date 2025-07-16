# app/backends.py

from django.contrib.auth.backends import BaseBackend
from .models import Concessionaria

class ConcessionariaBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Concessionaria.objects.get(email=email)
            if user.check_password(password):
                return user
        except Concessionaria.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Concessionaria.objects.get(pk=user_id)
        except Concessionaria.DoesNotExist:
            return None