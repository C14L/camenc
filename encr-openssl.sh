#!/bin/bash

EXECDIR=/home/pi/dev/camenc
DATADIR=/home/pi/temp/raspicam
INTERVAL=1
#PICSIZE=1920x1080
PICSIZE=960x540
CONFFILE=~/.camenc
POSTURL=http://192.168.0.94:8000/add

#echo "Writing images to: $DATADIR until Ctrl+C is pressed ..."

# Load or create a hash identifier for this device.
#
[ -f $CONFFILE ] && \
    HASH=$(cat $CONFFILE) || \
    HASH=$(echo "$(date) $(cat /sys/class/net/*/address)" | md5sum | cut -f1 -d' ') && \
    echo $HASH > $CONFFILE

# http --form POST http://192.168.0.94:8000/add uid=123abc456def file@webcam-1523646646.jpg.enc

# Take pictures forever.
#
while [ true ]; do

  FILENAME=$DATADIR/webcam-`date +%s`.jpg.enc
  
  fswebcam -r $PICSIZE --skip 2 --jpeg 80 - | \
    openssl smime \
        -encrypt \
        -binary \
        -aes-256-cbc \
        -outform DER $EXECDIR/public-key.pem | \
      tee $FILENAME >/dev/null 2>$DATADIR/error.log

  http --form POST $POSTURL uid=$HASH file@$FILENAME

  #echo "File written: $FILENAME"
  sleep $INTERVAL
done

