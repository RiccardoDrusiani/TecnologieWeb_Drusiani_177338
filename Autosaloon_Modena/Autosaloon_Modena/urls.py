"""
URL configuration for Autosaloon_Modena project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django_registration.backends.one_step import urls as registration_urls
from django.conf import settings
from django.conf.urls.static import static
from django_registration.backends.one_step.views import RegistrationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.Autosalone.urls')),
    path('Autosalone/', include(('apps.Autosalone.urls', 'Autosalone'), namespace='Autosalone')),
    path('Utente/', include(('apps.Utente.urls', 'Utente'), namespace='Utente')),
    path('Concessionaria/', include(('apps.Concessionaria.urls', 'concessionaria'), namespace='concessionaria')),
    path('Auto/', include(('apps.Auto.urls', 'Auto'), namespace='Auto')),
    path('chat/', include(('apps.Chat.urls', 'Chat'), namespace='Chat')),
    # Registrazione utente con template personalizzato (anche su /accounts/register/)
    path('accounts/register/', RegistrationView.as_view(template_name='Utente/registration_form.html'), name='django_registration_register'),
    # Registrazione concessionaria con template personalizzato
    path('accounts/register/', RegistrationView.as_view(template_name='Concessionaria/registration_form.html'), name='register_concessionaria'),
    path("accounts/", include(registration_urls)),
    path("accounts/", include("django.contrib.auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
