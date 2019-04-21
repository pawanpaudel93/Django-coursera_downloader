from django.shortcuts import render, redirect
from .forms import DownloadForm
from django.views.generic import TemplateView
import base64
from b2blaze import B2
from decouple import config

class Home(TemplateView):
    template_name = 'download_engine/home.html'
    def post(self, request):
        form = DownloadForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            course_link = form.cleaned_data['course_link']
            # details = {'username': username, 'password': password, 'course_link': course_link}
            # encoded_dict = str(details).encode('utf-8')
            # base64_details = base64.b64encode(encoded_dict)
            request.session['email'] = email
            request.session['course_link'] = course_link
            try:
                course_title = [course_title for course_title in course_link.split('/') if '-' in course_title][0]
            except:
                course_title = [course_title for course_title in course_link.split('/')][4]
            return redirect('downloader', course_title=course_title)
            
    
    def get(self, request):
        form = DownloadForm()
        return render(request, self.template_name, {'form': form})

def downloading_file(request):
    return render(request, 'download_engine/downloading.html')

def courses_links(request):
    b2 = B2(key_id=config('B2_KEY_ID'), application_key=config('B2_APPLICATION_KEY'))
    bucket = b2.buckets.get('cdownloader')
    files = bucket.files.all()
    return render(request, 'download_engine/courses_links.html', {'files': files})