"""
ASGI config for Autosaloon_Modena project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from starlette.staticfiles import StaticFiles
from starlette.applications import Starlette
from starlette.routing import Mount


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Autosaloon_Modena.settings')

django_asgi_app = get_asgi_application()

from apps.Chat import routing as chat_routing

# Crea una Starlette app che monta i file statici
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
static_app = Starlette(routes=[
    Mount("/static", app=StaticFiles(directory=static_dir), name="static"),
    Mount("/", app=django_asgi_app),
])

application = ProtocolTypeRouter({
    "http": static_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat_routing.websocket_urlpatterns
        )
    ),
})
