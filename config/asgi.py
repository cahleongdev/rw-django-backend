import os

import django
from django.core.asgi import get_asgi_application

# Set Django settings before any other Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Import other Django components after setup
from django.urls import path

from app.consumers.messages import MessageConsumer

# Import consumers last
from app.consumers.notifications import NotificationConsumer
from app.middleware.token_auth import TokenAuthMiddleware

# Define the ASGI application
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddleware(
                URLRouter(
                    [
                        path("ws/messaging/", MessageConsumer.as_asgi()),
                        path("ws/notifications/", NotificationConsumer.as_asgi()),
                    ]
                ),
            ),
        ),
    }
)
