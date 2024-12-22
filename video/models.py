from django.db import models

class VideoType(models.Model):
    name = models.CharField(max_length=100)
    image= models.ImageField(upload_to="images/", default='', blank=True)
    description=models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name

class video(models.Model):
    cate = models.ForeignKey(VideoType, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    link = models.CharField(max_length=300)
    

    
