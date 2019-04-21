from django.db import models

class Form(models.Model):
    email = models.EmailField(max_length=50)
    course_link = models.CharField(max_length=100)
class Course_Url(models.Model):
    course_title = models.CharField(max_length=100)
    url = models.URLField(max_length=250)