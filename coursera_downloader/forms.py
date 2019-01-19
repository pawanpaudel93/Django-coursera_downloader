from django.forms import ModelForm
from django import forms
from download_engine.models import Form

class DownloadForm(ModelForm):
    coursera_username = forms.EmailField(
        required = True
    )
    course_link = forms.CharField(
        required = True
    )
    email = forms.EmailField(
        required = True
    )
    coursera_password = forms.CharField(
        required = True,
        strip=False,
        widget=forms.PasswordInput
    )
    class Meta:
        model = Form
        fields = ['email','coursera_username', 'coursera_password', 'course_link']