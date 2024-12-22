from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
class ForumModel(models.Model):
    title = models.CharField("Title", max_length=200)
    content = CKEditor5Field("Content", config_name='extends')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    replies = models.IntegerField(default=0, blank=True)
    views = models.IntegerField(default=0, blank=True)
    publication_date = models.DateTimeField(auto_now_add=True)


class ReplyModel(models.Model):
    forum = models.ForeignKey(ForumModel, on_delete=models.CASCADE)
    content = CKEditor5Field("Content", config_name="extends")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.IntegerField(default=0, blank=True)
    unlike = models.IntegerField(default=0, blank=True)
    publication_date = models.DateTimeField(auto_now_add=True)