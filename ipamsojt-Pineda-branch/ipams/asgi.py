"""
ASGI config for ipams project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.routing import get_default_application

from channels.auth import AuthMiddlewareStack
from notifications.routing import websocket_urlpatterns
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ipams.settings')
django.setup()
application = get_default_application()
