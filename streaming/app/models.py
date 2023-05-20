from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MiModelo(models.Model):
    campo1 = models.CharField(max_length=50)
    campo2 = models.IntegerField()


class Template(models.Model):
    
    template_number = models.IntegerField(default=0)
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_frame_url = models.CharField(max_length=255, blank=True)


    def __str__(self):
        return self.name
    

class Comment(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.content
    
