from django.shortcuts import render, redirect
from .forms import DownloadForm
from django.views.generic import TemplateView
import base64

class Home(TemplateView):
    template_name = 'download_engine/home.html'
    def post(self, request):
        form = DownloadForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['coursera_username']
            password = form.cleaned_data['coursera_password']
            course_link = form.cleaned_data['course_link']
            details = {'email': email, 'username': username, 'password': password,'course_link': course_link}
            encoded_dict = str(details).encode('utf-8')
            base64_details = base64.b64encode(encoded_dict)
            return redirect('downloader',slug=base64_details.decode('utf-8'))
            
    
    def get(self, request):
        form = DownloadForm()
        return render(request, self.template_name, {'form': form})