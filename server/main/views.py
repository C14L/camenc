import logging
import os
import re
import time

from datetime import datetime
from random import randint

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from .models import Cam
from .forms import CamForm


log = logging.getLogger(__name__)

PICS_DIR = settings.PICS_DIR
if not os.path.exists(PICS_DIR):
    os.mkdir(PICS_DIR, 0o755)

DOORMAN_LOGFILE = settings.DOORMAN_LOGFILE
DOORMAN_PING_LOGFILE = settings.DOORMAN_PING_LOGFILE

RE_VALID_UPLOAD_NAME = re.compile(r"^[a-z0-9]{6}-\d{10}\.jpg.enc$")
RE_VALID_UPLOAD_DIR = re.compile(r"^[a-zA-Z0-9]{32}$")
KiB = 1024
MAX_FILES = 20000  # Max number of files kept in the pics dir. Oldest files are deleted.


@login_required
def home(request, template="main/home.html"):
    doorman = list(get_doorman_log())
    doorman.reverse()

    cams = list(request.user.cams.all())
    pics = list(get_preview_files(cams[0].uid) if cams else [])
    pics.sort(reverse=True)

    context = {
        "doorman": doorman,
        "last_ping": get_doorman_last_ping(),
        "cams": cams,
        "pics": pics[:1000],
    }

    return render(request, template, context)


def get_preview_files(cam_id):
    d = os.path.join(PICS_DIR, cam_id, "preview")
    for f in os.listdir(d):
        if f.endswith(".jpg"):
            yield f


def get_cam_status(uid):
    return {
        "latest_post_date": datetime.now(),
        "oldest_post_date": datetime.now(),
        "files_count": 48396,
        "storage_gb_used": 2.13,
        "storage_gb_free": 0.87,
        "health_percent": 100,
        # ...
    }


###########################################################
# Endpoints used by the Raspis
###########################################################


@csrf_exempt
def doorman_add(request):
    """Receive status from doorman (door opening, movement detection, light, etc.).
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kind = request.POST.get("kind", None)
    data = request.POST.get("data", None)

    if kind is None or data is None:
        return HttpResponseBadRequest()

    if kind == "ping":
        with open(DOORMAN_PING_LOGFILE, "a") as fh:
            fh.write("%s\n" % (now,))
    else:
        with open(DOORMAN_LOGFILE, "a") as fh:
            fh.write("%s %s %s\n" % (now, kind, data))

    return HttpResponse()


@csrf_exempt
def add(request):
    try:
        upload = request.FILES["file"]
    except MultiValueDictKeyError:
        return HttpResponseBadRequest("No upload file.")

    uid = request.POST["uid"][:32]

    log.info("uid, upload.name: %s %s", uid, upload.name)

    upload_ext = upload.name[-3:]

    if upload_ext == "enc":
        name_tpl = "{}.jpg.enc"
    elif upload_ext == "jpg":
        name_tpl = "{}.jpg"
    else:
        log.error("Invalid upload file name.")
        return HttpResponseBadRequest("Invalid upload file name.")

    if not RE_VALID_UPLOAD_DIR.match(uid):
        log.error("Invalid upload data.")
        return HttpResponseBadRequest("Invalid upload data.")

    base_dir = os.path.join(PICS_DIR, uid)
    data_dir = os.path.join(base_dir, "full")
    thumb_dir = os.path.join(base_dir, "preview")

    if not os.path.exists(base_dir):
        os.mkdir(base_dir, 0o755)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir, 0o755)
    if not os.path.exists(thumb_dir):
        os.mkdir(thumb_dir, 0o755)
    if os.path.exists(os.path.join(base_dir, ".upload-disabled")):
        log.error("Upload disabled.")
        return HttpResponseNotAllowed("Upload disabled.")

    file_name = name_tpl.format(datetime.now().isoformat("T"))
    full_path = os.path.join(data_dir, file_name)
    thumb_path = os.path.join(thumb_dir, file_name)

    if upload_ext == "enc":
        target_f = full_path
    elif upload_ext == "jpg":
        target_f = thumb_path

    with open(target_f, "wb+") as fh:
        for chunk in upload.chunks():
            fh.write(chunk)

    # Integrity check: verify file size if reasonable for an image.
    if upload_ext == "enc":
        file_size = os.path.getsize(full_path)  # Bytes
        if file_size > 1000 * KiB:
            os.remove(full_path)  # delete large files.
            log.error("File size too large for a camenc image.")
            return HttpResponseBadRequest("File size too large for a camenc image.")

    return HttpResponse()


def get_doorman_log():
    """Get doorman log entries.

    Returns:
        list of tuple: datetime, log message
    """
    try:
        with open(DOORMAN_LOGFILE, "r") as fh:
            for row in fh:
                if row and len(row) > 20:
                    yield (row[:19], row[20:])
    except FileNotFoundError:
        pass


def get_doorman_pings():
    try:
        with open(DOORMAN_PING_LOGFILE, "r") as fh:
            for row in fh:
                if row:
                    yield row
    except FileNotFoundError:
        pass


def get_doorman_last_ping():
    d = list(get_doorman_pings())
    return d[-1] if d else ""
