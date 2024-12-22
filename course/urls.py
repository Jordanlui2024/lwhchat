from django.urls import path
from . import views

urlpatterns = [
    path('', views.courseListPage, name="ebookListPage"),
    path('download/<int:pk>', views.downloadFile, name='downloadPage'),
]
