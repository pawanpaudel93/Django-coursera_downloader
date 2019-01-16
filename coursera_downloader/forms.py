from django.forms import ModelForm
from django import forms
from download_engine.models import Form

class DownloadForm(ModelForm):
    class Meta:
        model = Form
        fields = ['username', 'password', 'course_link']