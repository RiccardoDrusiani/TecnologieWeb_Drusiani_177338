# python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class ConcessionariaManager(BaseUserManager):
    def create_concessionaria(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("La concessionaria deve avere un'email")
        email = self.normalize_email(email)
        concessionaria = self.model(email=email, **extra_fields)
        concessionaria.set_password(password)
        concessionaria.save(using=self._db)
        return concessionaria

class Concessionaria(AbstractBaseUser):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)
    indirizzo = models.TextField()
    telefono = models.CharField(max_length=15)
    partita_iva = models.CharField(max_length=11, unique=True)
    codice_fiscale = models.CharField(max_length=16, unique=True)

    objects = ConcessionariaManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'partita_iva', 'codice_fiscale']

    def __str__(self):
        return self.nome
