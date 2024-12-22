import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from room.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangochat.settings')
http_response_app = get_asgi_application()

application = ProtocolTypeRouter(
    {"http": http_response_app, "websocket": URLRouter(websocket_urlpatterns)}
)
