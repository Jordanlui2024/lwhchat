from django.urls import path
from . import views

urlpatterns = [
    path("", views.roomsPage, name="roomsPage"),
    path("<slug:slug>/", views.chatroomPage, name="chatroomPage")
]