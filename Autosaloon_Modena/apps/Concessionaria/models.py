# python
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.text import slugify

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
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)

    objects = ConcessionariaManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'partita_iva', 'codice_fiscale']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nome)
            unique_slug = base_slug
            num = 1
            while Concessionaria.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)
