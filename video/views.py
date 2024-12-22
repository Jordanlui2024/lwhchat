from django.shortcuts import render
from .models import video, VideoType

def videoListPage(request):
    videoList = VideoType.objects.all()
    return render(request, "video/videoListPage.html", {'videoList':videoList})

def videoPage(request, slug):
    videoType = VideoType.objects.get(slug = slug)
    youtubes = video.objects.filter(cate=videoType)
    return render(request, "video/videoPage.html", {'youtubes': youtubes})