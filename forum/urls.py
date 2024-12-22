from django.urls import path
from . import views

urlpatterns = [
    path("forumlist/<int:page>/", views.forumListPage, name="forumListPage"),
    path("forumid/<int:forum_id>/<int:page>/", views.forumReplyPage, name="forumReplyPage"),
    path("article/", views.forumArticlePage , name="articlePage"),
    path("reply/<int:forum_id>/<int:page>/", views.forumUpdateReplyPage, name="updateReplyPage"),
]
