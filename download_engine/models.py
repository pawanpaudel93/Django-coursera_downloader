from django.db import models

from django.db import models

class Form(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    course_link = models.CharField(max_length=100)