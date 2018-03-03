#!/bin/bash

EXECDIR=/home/pi/dev/camenc
DATADIR=/home/pi/temp/raspicam
INTERVAL=3
#PICSIZE=1920x1080
PICSIZE=960x540

#echo "Writing images to: $DATADIR until Ctrl+C is pressed ..."

while [ true ]; do

  FILENAME=$DATADIR/webcam-`date +%s`.jpg.enc
  
  fswebcam -r $PICSIZE --skip 2 --jpeg 80 - | \
    openssl smime \
        -encrypt \
        -binary \
        -aes-256-cbc \
        -outform DER $EXECDIR/public-key.pem | \
      tee $FILENAME >/dev/null 2>$DATADIR/error.log

  #echo "File written: $FILENAME"
  sleep $INTERVAL
done

