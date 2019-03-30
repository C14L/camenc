#!/bin/bash

EXECDIR=/home/pi/dev/camenc/camera
DATADIR=/home/pi/temp/raspicam
ERRLOG=$DATADIR/error.log

INTERVAL=2

PICSIZE=1920x1080
#PICSIZE=960x540

THUMBSIZE=48x27

CONFFILE=~/.camenc

#POSTURL="http://192.168.0.94:7700/add"
POSTURL="https://c14l.com/camenc/add"

#echo "Writing images to: $DATADIR until Ctrl+C is pressed ..."

# Load or create a hash identifier for this device.
#
[ -f $CONFFILE ] && \
    HASH=$(cat $CONFFILE) || \
    HASH=$(echo "$(date) $(cat /sys/class/net/*/address)" | md5sum | cut -f1 -d' ') && \
    echo $HASH > $CONFFILE

# Take pictures forever.
#
while [ true ]; do

    THUMBFILE=$DATADIR/webcam-`date +%s`.preview.jpg
    FILENAME=$DATADIR/webcam-`date +%s`.jpg.enc

    fswebcam -r $PICSIZE --skip 2 --jpeg 80 - | tee                                                 \
        >(                                                                                          \
            convert -resize $THUMBSIZE - - > $THUMBFILE 2>$ERRLOG &&                                \
            curl -m5 -F "uid=$HASH" -F "file=@$THUMBFILE" $POSTURL                                  \
        )                                                                                           \
        >(                                                                                          \
            openssl smime -encrypt -binary -aes-256-cbc -outform DER "$EXECDIR/public-key-a.pem" |  \
            openssl smime -encrypt -binary -aes-256-cbc -outform DER "$EXECDIR/public-key-b.pem" |  \
            tee $FILENAME >/dev/null &&                                                             \
            curl -m5 -F "uid=$HASH" -F "file=@$FILENAME" $POSTURL                                   \
        )                                                                                           \
        >/dev/null 2>$ERRLOG

    sleep $INTERVAL
    rm -f "$THUMBFILE"
    rm -f "$FILENAME"

done

