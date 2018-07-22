import logging
import os
import re
import time

from datetime import datetime
from random import randint

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseNotAllowed, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Cam
from .forms import CamForm


log = logging.getLogger(__name__)

# PICS_DIR = os.path.join(settings.BASE_DIR, 'pics')
PICS_DIR = '/tmp/pics'
if not os.path.exists(PICS_DIR):
    os.mkdir(PICS_DIR, 0o755)

RE_VALID_UPLOAD_NAME = re.compile(r'^[a-z0-9]{6}-\d{10}\.jpg.enc$')
RE_VALID_UPLOAD_DIR = re.compile(r'^[a-zA-Z0-9]{32}$')
KiB = 1024
MAX_FILES = 20000  # Max number of files kept in the pics dir. Oldest files are deleted.


@login_required
def home(request, template='main/home.html'):
    if request.method == 'POST':
        if request.POST.get('pk'):
            cam = Cam.objects.get(pk=request.POST['pk'])
            form = CamForm(request.POST, instance=cam)
            form.save()
            messages.success(request, 'Cam aktualisiert.')
        else:
            form = CamForm(request.POST)
            cam = form.save(commit=False)
            cam.user = request.user
            cam.save()
            messages.success(request, 'Cam neu angelegt.')
        return HttpResponseRedirect('/')

    cams = [
        {
            'data': x,
            'form': CamForm(instance=x),
            'status': get_cam_status(x.uid),
        }
        for x in Cam.objects.filter(user=request.user)
    ]

    context = {
        'cams': cams,
        'new_cam_form': CamForm(),
    }

    return render(request, template, context)


def get_cam_status(uid):
    return {
        'latest_post_date': datetime.now(),
        'oldest_post_date': datetime.now(),
        'files_count': 48396,
        'storage_gb_used': 2.13,
        'storage_gb_free': 0.87,
        'health_percent': 100,
        # ...
    }


@csrf_exempt
def add(request):
    upload = request.FILES['file']
    uid = request.POST['uid'][:32]

    log.info('uid, upload.name: %s %s', uid, upload.name)

    if not RE_VALID_UPLOAD_DIR.match(uid):
        return HttpResponseBadRequest('Invalid upload data.')
    #if not RE_VALID_UPLOAD_NAME.match(upload.name):
    #     return HttpResponseBadRequest('Invalid upload data.')

    data_dir = os.path.join(PICS_DIR, uid)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir, 0o755)
    if os.path.exists(os.path.join(data_dir, '.upload-disabled')):
        print("Upload disabled.")
        return HttpResponseNotAllowed('Upload disabled.')

    file_name = '{}.jpg.enc'.format(
        int(time.time() * 1000)
    )
    full_path = os.path.join(data_dir, file_name)
    with open(full_path, 'wb+') as fh:
        for chunk in upload.chunks():
            fh.write(chunk)

    # Randomly every 10th request check storage constrains.
    if randint(0, 9) == 5:
        enforce_storage_constrains(data_dir, full_path)

    # Integrity check: verify file size if reasonable for an image.
    file_size = os.path.getsize(full_path)  # Bytes
    if file_size < 10 * KiB:
        return HttpResponseBadRequest('File size too small for a camenc image.')
    if file_size > 500 * KiB:
        os.remove(full_path)  # delete large files.
        return HttpResponseBadRequest('File size too large for a camenc image.')

    return HttpResponse()


def enforce_storage_constrains(data_dir, full_path):
    # Keep total file storage size within "max_gb".
    pass

    # Keep only files equal or younger than "max_days".
    pass

    # Keep number of files within "max_files".
    diff = len(os.listdir(data_dir)) - MAX_FILES
    if diff > 0:
        # Delete `diff` oldest files.
        li = [
            (x.path, int(x.stat().st_ctime))
            for x in os.path.scandir(data_dir)
            if x.path.endswith('.enc')
        ]
        li.sort(key=lambda x: x[1])
        li = li[:diff]  # only need the files with lowest timestamp vals
        for f, _t in li:
            os.remove(f)

    # Integrity check: verify file size if reasonable for an image.
    file_size = os.path.getsize(full_path)  # Bytes
    if file_size < 10 * KiB:
        os.remove(full_path)  # delete faulty files.
        print("File size too small for a camenc image: {} Bytes".format(file_size))
        return HttpResponseBadRequest('File size too small for a camenc image.')
    if file_size > 500 * KiB:
        os.remove(full_path)  # delete faulty files.
        print("File size too large for a camenc image: {} Bytes".format(file_size))
        return HttpResponseBadRequest('File size too large for a camenc image.')

    return HttpResponse()

