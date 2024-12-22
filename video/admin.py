from django.contrib import admin
from .models import VideoType, video

class VideoAdmin(admin.ModelAdmin):
    type_list = ('video', "video_type")
    
admin.site.register(video, VideoAdmin)
admin.site.register(VideoType)   
