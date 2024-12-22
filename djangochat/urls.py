from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static

from django.conf import settings
from django.views.static import serve



urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    path('', include('core.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
    path('rooms/', include("room.urls")),
    path('forum/', include('forum.urls')),
    path('contactus/', include('contactus.urls')),
    path('video/', include('video.urls')),
    path('ebook/', include("course.urls")),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
