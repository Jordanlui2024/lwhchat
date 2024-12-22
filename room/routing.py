from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/<str:room_name>/<str:user_name>/', consumers.ChatConsumer.as_asgi()),

]