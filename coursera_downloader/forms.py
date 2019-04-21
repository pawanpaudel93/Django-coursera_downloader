from django.forms import ModelForm
from django import forms
from download_engine.models import Form

class DownloadForm(ModelForm):
    course_link = forms.CharField(
        required = True
    )
    email = forms.EmailField(
        required = True
    )
    class Meta:
        model = Form
        fields = ['email', 'course_link']