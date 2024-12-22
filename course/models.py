from django.db import models

class CourseModel(models.Model):
    name = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to='images/', default="", blank=True)
    description=models.TextField(blank=True)
    image = models.ImageField(upload_to="images/", default="", blank=True)
    def __str__(self):
        return self.name

# class CourseDetailModel(models.Model):
#     file = models.ForeignKey(CourseModel, on_delete=models.CASCADE),    
#     name = models.CharField(max_length=100),
#     description=models.CharField(max_length=200, blank=True),
#     image = models.ImageField(upload_to="images/"),