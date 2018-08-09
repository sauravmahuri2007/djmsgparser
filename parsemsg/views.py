import json
import os
import unicodedata
import re
import string
import subprocess
from shutil import rmtree

from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.generic import View

from .forms import UploadForm
from webmsg_config import UPLOAD_PATH, MSG_DIR_NAME, MSG_DIR, JSON_FILE_NAME, TEXT_FILE_NAME, PARSE_FORMAT


def get_upload_path(file_name):
    return os.path.join(UPLOAD_PATH, file_name)


def get_parsed_file_path(file_name):
    """
    Returns the parse file absolute path from which the file will be further read and displayed in browser
    :param file_name: name of the file. eg: my_msg_file
    """
    if PARSE_FORMAT == 'json':
        file_format_name = JSON_FILE_NAME
    else:
        file_format_name = TEXT_FILE_NAME
    return os.path.join(os.path.join(MSG_DIR, file_name), file_format_name)


def save_memory_file(memory_file, path):
    with open(path, 'wb') as f:
        for chunk in memory_file.chunks():
            f.write(chunk)
    return True


def normalize_filename(file_name):
    """
    Normalizes given file name by stripping out accent characters and other invalid file name characters.
    """
    allowed_chars = '{0}{1}-_.'.format(string.ascii_letters, string.digits)
    cleaned_file_name = unicodedata.normalize('NFKD', file_name).encode('ascii', 'ignore')
    cleaned_file_name = cleaned_file_name.decode('ascii', 'ignore')
    return ''.join(char for char in cleaned_file_name if char in allowed_chars)


def parse_msg_file(file_path):
    """
    parse the .msg file into a json file. The file will be saved as 'file_path'.json format
    :param file_path: the absolute path of the .msg file
    """
    upload_dir = os.path.dirname(file_path)  # eg: the directory where the .msg file was saved
    msg_dir = os.path.join(upload_dir, MSG_DIR_NAME)  # to create all parsed msg file here
    file_name = os.path.split(file_path)[1]  # name of the file
    try:
        os.chdir(msg_dir)  # to make sure the parsed file will be created on this directory
    except FileNotFoundError:
        os.mkdir(msg_dir)
        os.chdir(msg_dir)
    if os.path.exists(os.path.join(msg_dir, file_name)):
        # delete if the directory for the file_name already exists
        rmtree(os.path.join(msg_dir, file_name))
    format = '--' + PARSE_FORMAT
    # 'ExtractMsg.py --use-file-name my_msg_file --json /path/of/msg/file'
    output = subprocess.check_output(['ExtractMsg.py', '--use-file-name', file_name, format, file_path])
    return True


def delete_msg_file(file_path):
    """
    deletes the .msg file which is saved at 'file_path' and parsed already to save server space.
    Call this function only after saving and parsing .msg file.
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return False
    return True


def fix_urls(text):
    pat_url = re.compile(  r'''
                     (?x)( # verbose identify URLs within text
         (http|https|ftp|gopher) # make sure we find a resource type
                       :// # ...needs to be followed by colon-slash-slash
            (\w+[:.]?){2,} # at least two domain groups, e.g. (gnosis.)(cx)
                      (/?| # could be just the domain name (maybe w/ slash)
                [^ \n\r"]+ # or stuff then space, newline, tab, quote
                    [\w/]) # resource name ends in alphanumeric or slash
         (?=[\s\.,>)'"\]]) # assert: followed by white or clause ending
                         ) # end of match group
                           ''')
    pat_email = re.compile(r'''
                    (?xm)  # verbose identify URLs in text (and multiline)
                 (?=^.{11} # Mail header matcher
         (?<!Message-ID:|  # rule out Message-ID's as best possible
             In-Reply-To)) # ...and also In-Reply-To
                    (.*?)( # must grab to email to allow prior lookbehind
        ([A-Za-z0-9-]+\.)? # maybe an initial part: DAVID.mertz@gnosis.cx
             [A-Za-z0-9-]+ # definitely some local user: MERTZ@gnosis.cx
                         @ # ...needs an at sign in the middle
              (\w+\.?){2,} # at least two domain groups, e.g. (gnosis.)(cx)
         (?=[\s\.,>)'"\]]) # assert: followed by white or clause ending
                         ) # end of match group
                           ''')

    for url in re.findall(pat_url, text):
        # text = text.replace(url[0], '<a href="%(url)s">%(url)s</a>' % {"url" : url[0]})
        rep_url = url[0].replace('<', '').replace('>', '')
        if re.search(r'jpg|jpeg|png|bmp|gif|jif|tiff', rep_url[-5:].lower()):
            text = text.replace(rep_url, 'img src="%(url)s"' % {"url": rep_url})
        else:
            text = text.replace(rep_url, 'a href="%(url)s">link</a' % {"url" : rep_url})

    # for email in re.findall(pat_email, text):
    #     rep_url = email[0].replace('<', '').replace('>', '')
    #     text = text.replace(rep_url, 'a href="mailto:%(email)s">%(email)s</a' % {"email" : rep_url})

    return text


class UploadMsg(View):
    """
    View responsible for uploading, parsing the .msg file and saving it into human readable format
    """

    template_name = 'upload_msg.html'

    def get(self, request, *args, **kwargs):
        upload_form = UploadForm()
        return render(request, template_name=self.template_name, context={'form': upload_form})

    def post(self, request, *args, **kwargs):
        form = UploadForm(request.POST, request.FILES)
        if not form.is_valid():
            error = form.errors.as_json()
            return render(request, template_name=self.template_name, context={'form': form, 'error': error})
        msg_file = request.FILES.get('msg_file')  # file object
        if not msg_file.name.lower().endswith('.msg'):
            error = 'Please upload a valid .msg file'
            return render(request, template_name=self.template_name, context={'form': form, 'error': error})
        file_name = request.POST.get('file_name') or msg_file.name

        # just the normalized file_name in lower case
        file_name = normalize_filename(file_name.lower().rsplit('.msg')[0])
        file_path = get_upload_path(file_name)
        save_memory_file(msg_file, file_path)
        parse_msg_file(file_path)
        delete_msg_file(file_path)
        return HttpResponseRedirect(reverse('show_msg', kwargs={'file_name': file_name}))


class ShowMsg(View):
    """
    View responsible for showing the parsed .msg file.
    """

    template_name = 'show_msg.html'

    def get(self, request, *args, **kwargs):
        file_name = kwargs.get('file_name')
        parsed_file_path = get_parsed_file_path(file_name)
        with open(parsed_file_path, 'r') as f:
            txt = f.read()
        context = {}
        try:
            msg = json.loads(txt)  # loading the json into dict
            context['is_json'] = True
            msg['body'] = fix_urls(msg.get('body', ''))
        except (ValueError):
            msg = fix_urls(txt)
        context['msg'] = msg
        return render(request, self.template_name, context)
