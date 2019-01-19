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
            # details = {'username': username, 'password': password, 'course_link': course_link}
            # encoded_dict = str(details).encode('utf-8')
            # base64_details = base64.b64encode(encoded_dict)
            request.session['email'] = email
            request.session['username'] = username
            request.session['password'] = password
            request.session['course_link'] = course_link
            course_title = [course_title for course_title in course_link.split('/') if '-' in course_title][0]
            return redirect('downloader', course_title=course_title)
            
    
    def get(self, request):
        form = DownloadForm()
        return render(request, self.template_name, {'form': form})

def downloading_file(request):
    return render(request, 'download_engine/downloading.html')