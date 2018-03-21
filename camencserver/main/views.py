import os.path
import re

from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, \
                        HttpResponseNotFound, \
                        HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


PICS_DIR = os.path.join(settings.BASE_DIR, 'pics')

RE_VALID_UPLOAD_NAME = re.compile(r'^[a-z0-9]{32}$')

KiB = 1024


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


@csrf_exempt
def add(request):
    upload = request.FILES['file']

    if not RE_VALID_UPLOAD_NAME.match(upload.name):
        return HttpResponseBadRequest('Invalid upload data.')

    data_dir = os.path.join(PICS_DIR, upload.name)

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    if os.path.exists(os.path.join(data_dir, '.upload-disabled')):
        return HttpResponseNotAllowed('Upload disabled.')

    file_name = str(int(datetime.timestamp(datetime.utcnow()) * 1000))

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

