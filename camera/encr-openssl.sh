#!/bin/bash

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# In regular intervals, take a picture. Encrypt it with the public keys found
# in the same directory. Simultaneously crate a thumbnail size version of the
# same picture unencrypted. Post both files to the /camenc/add route. Finally
# delete the files.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

EXECDIR=/home/pi/camenc/camera
DATADIR=/home/pi/temp/raspicam
ERRLOG=$DATADIR/error.log

INTERVAL=5  # seconds to wait between photos

PICSIZE=1920x1080
#PICSIZE=960x540

THUMBSIZE=48x27

CONFFILE=~/.camenc

#POSTURL="http://192.168.0.94:7700/add"  # local testing
POSTURL="https://c14l.com/camenc/add"

# Load or create a hash identifier for this device. This is the directory
# where uploaded pictures from this device are stored.
[ -f $CONFFILE ] && \
    HASH=$(cat $CONFFILE) || \
    HASH=$(echo "$(date) $(cat /sys/class/net/*/address)" | md5sum | cut -f1 -d' ') && \
    echo $HASH > $CONFFILE

# Take pictures forever.
while [ true ]; do

    THUMBFILE=$DATADIR/webcam-`date +%s`.preview.jpg
    FILENAME=$DATADIR/webcam-`date +%s`.jpg.enc

    fswebcam -r $PICSIZE --skip 2 --jpeg 80 - 2>/dev/null | tee                                     \
        >(                                                                                          \
            convert -resize $THUMBSIZE - - > $THUMBFILE 2>$ERRLOG &&                                \
            curl -m5 -F "uid=$HASH" -F "file=@$THUMBFILE" $POSTURL 2>$ERRLOG &&                     \
            rm -f $THUMBFILE 2>$ERRLOG                                                              \
        )                                                                                           \
        >(                                                                                          \
            openssl smime -encrypt -binary -aes-256-cbc -outform DER "$EXECDIR/public-key-a.pem" |  \
            openssl smime -encrypt -binary -aes-256-cbc -outform DER "$EXECDIR/public-key-b.pem" |  \
            tee $FILENAME >/dev/null 2>$ERRLOG &&                                                   \
            curl -m5 -F "uid=$HASH" -F "file=@$FILENAME" $POSTURL 2>$ERRLOG &&                      \
            rm -f "$FILENAME" 2>$ERRLOG                                                             \
        )                                                                                           \
        >/dev/null 2>$ERRLOG

    sleep $INTERVAL

done

