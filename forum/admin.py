from django.contrib import admin

from .models import ForumModel, ReplyModel
admin.site.register(ForumModel)
admin.site.register(ReplyModel)
