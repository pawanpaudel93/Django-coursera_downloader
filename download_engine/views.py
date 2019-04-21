from django.shortcuts import render
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.shortcuts import render, redirect
from coursera_downloader.settings.base import PROJECT_ROOT
from splinter import Browser
import base64, getpass, json, os, re, requests, sys, time, shutil
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options 
from b2blaze import B2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config
from django.http import HttpResponse
from .models import Course_Url

# some constants
loading_time = 2
homepage='https://www.coursera.org'
resolution = {'low':'360','med':'540','hi':'720'}
chosen_res = 'hi'
initial_dirname = os.getcwd()
# executable_path = {'executable_path': PROJECT_ROOT+"/static/coursera_downloader/chromedriver"}
# browser = Browser('chrome', **executable_path)

####

def read_text_file(file_name):
    f = open(file_name, "r")
    print("file being read: " + file_name + "\n")  
    return f.read()

def file_create(file_name, str_data):
    try:  
        f = open(file_name, "w")
        f.writelines(str(str_data))
        f.close()
    except IOError:        
        file_name = file_name.split(os.sep)[-1]
        f = open(file_name, "w")
        f.writelines(str(str_data))
        f.close()
    print("file created: " + file_name + "\n")
    
def convert_content(file_contents):
    replacement = re.sub(r'([\d]+)\.([\d]+)', r'\1,\2', file_contents)
    replacement = re.sub(r'WEBVTT\n\n', '', replacement)
    replacement = re.sub(r'^\d+\n', '', replacement)
    replacement = re.sub(r'\n\d+\n', '\n', replacement)
    return replacement

def vtt_to_srt(file_name):
    
    file_contents = read_text_file(file_name)
    str_data = ""
    str_data = str_data + convert_content(file_contents)  
    file_name = file_name.replace(".vtt",".srt")
    print(file_name)
    file_create(file_name, str_data)

#####
def get_mp4_url(browser, lesson_url):
    
    if lesson_url not in browser.driver.current_url:
        browser.visit(homepage+lesson_url)
        time.sleep(loading_time)
        print('video playing will be paused in ' + str(loading_time) + ' seconds...')
        time.sleep(loading_time)
    try:
        browser.find_by_css('.cif-play-circle.cif-stack-2x')[0].click()
        browser.find_by_css('.cif-2x.cif-fw.cif-cog').click()
        browser.find_by_css('.cif-plus')[0].click()
        browser.find_by_css('button.rc-PlayToggle')[0].click()
    except:
        time.sleep(loading_time)
        try:
            browser.find_by_css('.cif-play-circle.cif-stack-2x')[0].click()
            browser.find_by_css('.cif-2x.cif-fw.cif-cog').click()
            browser.find_by_css('.cif-plus')[0].click()
            browser.find_by_css('button.rc-PlayToggle')[0].click()
        except:
            pass
        pass
    
    mp4 = browser.find_by_css('.vjs-tech')[0]
    mp4 = mp4['src']
    print('Link is: ', mp4)
    return mp4

def get_vtt_url(browser, lesson_url):
    if lesson_url not in browser.driver.current_url:
        browser.visit(homepage+lesson_url)
        time.sleep(loading_time)
    element = browser.find_by_css('.rc-VideoItemWithHighlighting')[0]
    vtt = BeautifulSoup(element.html, 'lxml').findAll('track')[0]['src']
    vtt = homepage + vtt
    return vtt

def vtt_downloader(browser, lesson_id, lesson_title, lesson_url):
    
    base_filename = lesson_id +'-'+ safe_text(lesson_title)    
    file_name = base_filename + '.vtt'
    file_exists = os.path.isfile(file_name)

    if file_exists:
        print('subtitle already downloaded.')
    else:
        vtt = get_vtt_url(browser, lesson_url)
        r = requests.get(vtt)
        f = open(file_name, 'w')
        f.write(r.text)
        f.close()
    vtt_to_srt(file_name)
        
def mp4_downloader(browser, lesson_id, lesson_title, lesson_url):
    
    mp4 = get_mp4_url(browser, lesson_url)
    base_filename = lesson_id +'-'+ safe_text(lesson_title)
    file_name = base_filename + '.mp4'

    downloaded_size = 0
    buffer_size = 1024

    print('requesting to download...')
    r = requests.get(mp4)
    content_length = r.headers['Content-Length']
    download_size = int(content_length)
    file_exists = os.path.isfile(file_name)
    
    if file_exists:
        
        if os.path.getsize(file_name) == download_size:
            print('mp4 already downloaded.')
            
    elif not file_exists:
        
        if r.status_code == 200:
            f = open(file_name, 'wb')
            for buffer in r.iter_content(buffer_size):
                f.write(buffer)
                downloaded_size += buffer_size
                status='\rdownloading...' + file_name + '>>> '
                status = status +str("{:.2f}".format(downloaded_size * 100. /download_size))+'%'
                sys.stdout.write(status)
                sys.stdout.flush()
            f.close()
        else:
            print('please check your connection..')

def safe_text(str_text):
    erasable = [':','/']
    for e in erasable:   
        str_text = str_text.replace(e, ' ')  
    while '  ' in str_text:
        str_text = str_text.replace('  ',' ')
    return str_text

def create_download_dir(dirname):
    
    dirname = safe_text(dirname)
    
    try:
        os.mkdir(dirname)
    except:
        pass
    
    os.chdir(dirname)
    print(os.getcwd())

def reformat_html(html, page_title):
    
    html = html.replace('<div class="rc-ItemBox rc-ReadingItem"><div class="item-box-content"><div>',
                  '<div class="rc-ItemBox rc-ReadingItem"><div class="item-box-content"><div> <h2 class="flex-1 align-self-center headline-4-text">'+page_title+'</h2>')

    html = html.replace('<div class="Box_120drhm-o_O-endJustify_b0g9ud-o_O-displayflex_poyjc" style="margin: 60px -60px -60px; border-top: 1px solid rgb(221, 221, 221); padding: 15px;"><div class="rc-ItemFeedback"><div class="rc-ItemFeedbackContent horizontal-box"><div class="rc-Like"><div class="rc-LikeContent"><div><button class="c-button-icon" aria-pressed="false" aria-label="Like"><i class="fa cif-thumbs-o-up" aria-hidden="true"></i></button></div><span></span></div></div><div class="rc-Dislike"><div class="rc-LikeContent"><div><button class="c-button-icon" aria-pressed="false" aria-label="Dislike"><i class="cif-thumbs-o-down" aria-hidden="true"></i></button></div><span></span></div></div><div class="rc-Flag"><div class="rc-FlagContent"><div><button class="c-button-icon" aria-pressed="false" aria-label="Report problem"><i class="cif-flag-o" aria-hidden="true"></i></button></div><span></span></div></div></div></div></div></div></div>','')
    
    return html

def write_html(base_filename, html):
    
    html = reformat_html(html, base_filename)
    file_name = base_filename + '.html'
    f = open(file_name, 'w')
    html = '<html><head><link href="https://d3njjcbhbojbot.cloudfront.net/webapps/builds/ondemand/app.07c9f4ac0583c6e2d2d1.css" rel="stylesheet"></head><body>'+html+'</body></html>'
    f.write(html)
    f.close()
    
def html_downloader(browser,lesson_id, lesson_title, lesson_url):
    
    if lesson_url not in browser.driver.current_url:
        browser.visit(homepage+lesson_url)
        time.sleep(loading_time)
    try:
        html = browser.find_by_css('div.item-page-content').html
        print('got reading item')
    except:
        html ='no content scraped.'
        pass
    
    base_filename = lesson_id +'-'+ safe_text(lesson_title)
    write_html(base_filename, html)
    
    return

def check_html_reading(browser, lesson_id, lesson_title, lesson_url):
    
    base_filename = lesson_id +'-'+ safe_text(lesson_title)
    file_name = base_filename + '.html'
    
    file_exists = os.path.isfile(file_name)
    if file_exists:
        print('html already downloaded.')
    else:
        html_downloader(browser, lesson_id, lesson_title, lesson_url)

def button_click(browser, text_):
    try:
        buttons = browser.find_by_tag('button')
        for button in buttons:
            if button.text == text_:
                print(text_)
                button.click()
                break
    except:
        pass

def reformat_html_quiz(html, page_title):    
    # quiz
    html = html.replace('<div class="header-back-arrow"><button class="back nostyle" role="button" tabindex="0"><i class="cif-back headline-2-text"></i><span class="screenreader-only">Back</span></button></div>',
                        '')
    html = html.replace('<div data-rc="ItemFeedback" class="c-quiz-item-feedback"><div data-reactroot="" class="rc-ItemFeedback"><div class="rc-ItemFeedbackContent horizontal-box"><div class="rc-Like"><div class="rc-LikeContent"><div><button class="c-button-icon" aria-pressed="false" aria-label="Like"><i class="fa cif-thumbs-o-up" aria-hidden="true"></i></button></div><span></span></div></div><div class="rc-Dislike"><div class="rc-LikeContent"><div><button class="c-button-icon" aria-pressed="false" aria-label="Dislike"><i class="cif-thumbs-o-down" aria-hidden="true"></i></button></div><span></span></div></div><div class="rc-Flag"><div class="rc-FlagContent"><div><button class="c-button-icon" aria-pressed="false" aria-label="Report problem"><i class="cif-flag-o" aria-hidden="true"></i></button></div><span></span></div></div></div></div></div>',
                        '')
    
    return html

def write_html_quiz(base_filename, html):
    
    html = reformat_html_quiz(html, base_filename)
    file_name = base_filename + '.html'
    f = open(file_name, 'w')
    html = '<html><head><link href="https://d3njjcbhbojbot.cloudfront.net/webapps/builds/ondemand/app.07c9f4ac0583c6e2d2d1.css" rel="stylesheet"></head><body>'+html+'</body></html>'
    f.write(html)
    f.close()

def quiz_downloader(browser, lesson_id, lesson_title, lesson_url):
    if lesson_url not in browser.driver.current_url:
        # print(lesson_url)
        browser.visit(homepage+lesson_url)
        time.sleep(loading_time)
        
    button_click(browser, 'Continue')
    button_click(browser, 'Start')
    button_click(browser, 'Resume')
    button_click(browser, 'Start Quiz')
    
    try:
        time.sleep(loading_time)
        html = browser.find_by_css('div.bt3-row').html
        print('got quiz item')
        base_filename = lesson_id +'-'+ safe_text(lesson_title)
        write_html_quiz(base_filename, html)
    except:
        print('something wrong...')
        html ='no quiz content scraped.'
        pass

def check_quiz(browser, lesson_id, lesson_title, lesson_url):
    
    base_filename = lesson_id +'-'+ safe_text(lesson_title)
    file_name = base_filename + '.html'
    
    file_exists = os.path.isfile(file_name)
    if file_exists:
        print('quiz already downloaded.')
    else:
        quiz_downloader(browser, lesson_id, lesson_title, lesson_url)

## send download link mail
def send_mail(sendto, body, subject):
    fromaddr = config('EMAIL')
    toaddr = sendto
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Coursera Course Download Link for " + subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(fromaddr, config('EMAIL_PASS'))
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def downloader(request, course_title):
    # backblaze
    b2 = B2(key_id=config('B2_KEY_ID'), application_key=config('B2_APPLICATION_KEY'))
    bucket = b2.buckets.get('cdownloader')
    email, course_link = request.session['email'], request.session['course_link']
    details = {'email': email, 'course_link': course_link}
    # for popping the values in sessions
    request.session.pop('email', None)
    request.session.pop('course_link', None)
    request.session.pop('email_body', None)
    request.session.modified = True
    print('Details', details)
    try:
        course_title = [course_title for course_title in course_link.split('/') if '-' in course_title][0]
    except:
        course_title = [course_title for course_title in course_link.split('/')][4]
    try:
        file = bucket.files.get(file_name=course_title+'.zip')
        # request.session['email_body'] = "https://f000.backblazeb2.com/file/cdownloader/"+ course_title + '.zip'
        return redirect('downloading')
    except:
        print('Files not present on storage')
        opts = Options()
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--headless')
        opts.binary_location = "/app/.apt/usr/bin/google-chrome-stable"
        # executable_path = {'executable_path': "/home/pawan/PycharmProjects/Django-Coursera-Downloader/cdownloader/static/coursera_downloader/chromedriver"}
        # browser = Browser('chrome', **executable_path)
        browser = Browser('chrome', chrome_options=opts, headless=True)

        browser.visit('https://www.coursera.org/courses?authMode=login')
        time.sleep(loading_time)
        browser.find_by_css('.Button_1w8tm98-o_O-primary_cv02ee-o_O-md_1jvotax')[0].click()
        # button_click(browser, 'Log in with Facebook')
        time.sleep(loading_time)
        
        browser.windows.current = browser.windows[1]
        browser.fill('email', config('FB_EMAIL'))
        browser.fill('pass', config('FB_PASSWORD'))

        buttons = browser.find_by_tag('input')
        for button in buttons:
            if (button.value == 'Log In'):
                print(button.value)
                button.click()
                break
        # try:
        #     error = browser.find_by_id('login-form-error').text
        #     if(error=='Wrong email or password. Please try again!'):
        #         print('Wrong email or password. Please try again!')
        #         browser.quit()
        # except Exception as e:
        #     print('Error caught',e)
        # give the link of course in which you are enrolled and you want to download
        # course_link=details['course_link']
        # course_title = [course_title for course_title in course_link.split('/') if '-' in course_title][0]
        time.sleep(2*loading_time)
        browser.windows.current = browser.windows[0]

        lecture_homepage = browser.driver.current_url
        browser.visit(course_link)
        time.sleep(loading_time)
        # to enroll the selected courses
        # try:
        #     print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        #     enroll_button = browser.find_by_css('.Button_1w8tm98-o_O-default_s8ym6d-o_O-md_1jvotax')[0]
        #     time.sleep(3*loading_time)
        #     if browser.find_by_css('.rc-SubscriptionVPropFreeTrial'):
        #         print('Button-1')
        #         enroll_button.click()
        #         browser.find_by_id('enroll_subscribe_audit_button').click()
        #     elif browser.find_by_css('.enrollmentChoiceContainer'):
        #         print('Button-2')
        #         time.sleep(3*loading_time)
        #         enroll_button.click()
        #         browser.find_by_css('.cif-circle-thin.cif-stack-2x')[1].double_click()
        #         browser.find_by_id('course_enroll_modal_continue_button_button').click()
        #         browser.find_by_css('.primary.align-horizontal-center.cozy').click()
        # except:
        #     print('fail..................................................')

        create_download_dir(course_title)
        # find weeks
        week = browser.find_by_css('div.rc-WeekCollectionNavigationItem > div')
        anchors = BeautifulSoup(week.html, 'lxml').findAll('a', attrs={})
        weeks = []
        for a in anchors:
            weeks.append(a['href'])

        print(weeks, len(weeks))
        # video LINKS
        lessons_i = []
        lessons_t = []
        lessons_u = []
        w_digit = len(str(len(weeks)))
        for w in range(len(weeks)):
            
            print('collecting lessons title and urls...\n')    
            browser.visit(homepage + weeks[w])
            time.sleep(loading_time)
            w = w+1
            
            print('\nVisiting week: ' + str(w))
            time.sleep(loading_time)
            module_lessons = browser.find_by_css('div.rc-ModuleLessons')
            print()
            print('Week '+str(w)+' titles:')
            seq = 0
            for i, module_lesson in enumerate(module_lessons):

                lessons_title = module_lesson.find_by_xpath("//*[contains(@class,'rc-WeekItemName headline-1-text')]")

                for j, l in enumerate(lessons_title):
                    seq  += 1
                    lesson_id = str(w*100+seq).zfill(w_digit+2)
                    title = l.text.replace('\n',' ')
                    print(lesson_id, title)
                    title = safe_text(title)
                    lessons_t.append(title)
                    lessons_i.append(lesson_id)
            
            print()
            print('Week '+str(w)+' links:')    
            seq = 0

            for i, module_lesson in enumerate(module_lessons):

                lessons_url = module_lesson.find_by_tag('ul')
            
                for j, e in enumerate(lessons_url):
                    anchors = BeautifulSoup(e.html, 'lxml').findAll('a')
                    for k, a in enumerate(anchors):
                        seq += 1
                        lesson_id = str(w*100+seq).zfill(w_digit+2)
                        lesson_url = a['href']
                        print(lesson_id, lesson_url)
                        lessons_u.append(lesson_url)
                
            print()
        
        # Download Lecture Videos and Readings
        os.chdir(initial_dirname)
        os.chdir(safe_text(course_title))
        # lessons_i, lessons_u, lessons_t = list(set(lessons_i)), list(set(lessons_u)), list(set(lessons_t))
        print(lessons_i, lessons_u, lessons_t)
        lessons = zip(lessons_i, lessons_t, lessons_u)
        for a,b,c in lessons:
            print(a,b)
            first_word = b.split(' ')[0]
            print(first_word)
            
            if 'Video' in first_word:
                mp4_downloader(browser,a,b,c)
                vtt_downloader(browser,a,b,c)
                print()
                
            elif 'Quiz' in first_word:
                check_quiz(browser,a, b, c)
                print()        
            
            else:
                print('other resource')
                check_html_reading(browser,a,b,c)
                print()
                
            print()
        print('Resources downloaded to:\n'+os.getcwd())
        Resource_folder = os.getcwd() #Folder which is to be zipped
        os.chdir(initial_dirname)
        shutil.make_archive(os.getcwd()+'/'+course_title,'zip', Resource_folder)
        os.chdir(initial_dirname)
        
        ## for uploading to backblaze
        large_file = open(course_title+'.zip', 'rb')
        zipped_file = bucket.files.upload(contents=large_file,file_name=course_title+'.zip')
        print('The file is uploaded')
        
        # getting url of the file uploaded
        file_url = "https://f000.backblazeb2.com/file/cdownloader/"+ course_title + '.zip'
        
        # send mail to downloader
        body = "The download link is " + str(file_url)
        send_mail(details['email'], body, course_title)
        print('Email sent')
        
        # add urls to course_urls model
        url = Course_Urls(url=str(file_url), course_title=course_title)
        url.save()
        
        ## removing folders and zip
        shutil.rmtree(course_title, ignore_errors=True)
        
        # os.remove(course_title+'.zip')
        print('Files and folder has been removed as well')
        print(os.listdir(os.getcwd()))
        browser.quit()
        return redirect('downloading')