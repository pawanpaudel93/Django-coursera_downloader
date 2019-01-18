from django.forms import ModelForm
from django import forms
from download_engine.models import Form

class DownloadForm(ModelForm):
    class Meta:
        model = Form
        fields = ['email', 'coursera_username', 'coursera_password', 'course_link']