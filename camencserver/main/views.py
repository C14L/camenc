import logging
import os
import re

from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


log = logging.getLogger(__name__)

# PICS_DIR = os.path.join(settings.BASE_DIR, 'pics')
PICS_DIR = '/tmp/pics'
if not os.path.exists(PICS_DIR):
    os.mkdir(PICS_DIR, 0o755)

RE_VALID_UPLOAD_NAME = re.compile(r'^[a-z0-9]{6}-\d{10}\.jpg.enc$')

KiB = 1024

MAX_FILES = 20000  # Max number of files kept in the pics dir. Oldest files are deleted.


def home(request):
    return HttpResponse('This is the endpoint for camenc security camera image storage.')


@csrf_exempt
def add(request):
    upload = request.FILES['file']
    uid = request.POST['uid']

    log.info('uid, upload.name: ', uid, upload.name)

    # if not RE_VALID_UPLOAD_NAME.match(upload.name):
    #     return HttpResponseBadRequest('Invalid upload data.')

    data_dir = os.path.join(PICS_DIR, uid)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir, 0o755)
    if os.path.exists(os.path.join(data_dir, '.upload-disabled')):
        return HttpResponseNotAllowed('Upload disabled.')

    file_name = '{}.jpg.enc'.format(int(datetime.timestamp(datetime.utcnow()) * 1000))
    full_path = os.path.join(data_dir, file_name)
    with open(full_path, 'wb+') as fh:
        for chunk in upload.chunks():
            fh.write(chunk)

    # Integrity check: verify file size if reasonable for an image.
    file_size = os.path.getsize(full_path)  # Bytes
    if file_size < 10 * KiB:
        return HttpResponseBadRequest('File size too small for a camenc image.')
    if file_size > 500 * KiB:
        os.remove(full_path)  # delete large files.
        return HttpResponseBadRequest('File size too large for a camenc image.')

    # Keep number of files below maximum.
    diff = len(os.listdir(data_dir)) - MAX_FILES
    if diff > 0:
        # Delete `diff` oldest files.
        li = [
            (x.path, int(x.stat().st_ctime))
            for x in os.scandir(data_dir)
            if x.path.endswith('.enc')
        ]
        li.sort(key=lambda x: x[1])
        li = li[:diff]  # only need the files with lowest timestamp vals
        for f, t in li:
            os.remove(f)

    return HttpResponse()
