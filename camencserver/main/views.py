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


def hello(request):
    return HttpResponse('Hello!')


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

    return HttpResponse()


"""
Pairing via USB. On first start up, create 32 Bytes md5 string as
perpetual and unique ID for the cam.

Connect via USB to PC and use WebUSB to open website with setup
page. Auth using the md5 string.

Ask user for WLAN auth to setup the cam's WLAN via the Javascript
from the browser. If WLAN was already set up, offer option to
delete (not edit) old setting.

On startup, if md5 string and WLAN setup found and connection
possible, automatically start taking and uploading images.

Pipe images directly throught to the CURL upload command,
without touching the local disk.

----------

Uploads are always made using the same filename that consists of a
cam specific random 32 char string. Pics uploaded with that string
are placed in a sub-folder named with that string. Each filename
in that sub-folder has a timestamp as it's file name. That way, all
files posted from one device are always in one sub-folder, and all
pic files are timestamped on the server-side, so that the client
can't temper with the file's upload time.

"""
