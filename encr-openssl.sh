#!/bin/bash

DATADIR=$1

echo "Writing images to: $DATADIR until Ctrl+C is pressed ..."

while [ true ]; do
  FILENAME=$DATADIR/webcam-`date +%s`.jpg.enc
  fswebcam -r 1920x1080 --skip 20 --jpeg 80 - | \
    openssl smime -encrypt -binary -aes-256-cbc -outform DER public-key.pem | \
    tee $FILENAME >/dev/null 2>&1
  echo "File written: $FILENAME"
  sleep 1
done

