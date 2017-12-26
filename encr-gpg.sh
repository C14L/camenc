#!/bin/bash

JPGFILE=webcam-$(date +%s).jpg

fswebcam -r 1920x1080 --skip 20 --jpeg 80 - | gpg -ac --batch --passphrase 1234 | tee $JPGFILE.gpg


