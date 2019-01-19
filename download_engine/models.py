from django.db import models

class Form(models.Model):
    email = models.EmailField(max_length=50)
    coursera_username = models.EmailField(max_length=50)
    coursera_password = models.CharField(max_length=50)
    course_link = models.CharField(max_length=100)