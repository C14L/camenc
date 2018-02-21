#!/bin/bash

DATADIR=$2
INTERVAL=$1

echo "Writing images to: $DATADIR until Ctrl+C is pressed ..."

while [ true ]; do
  FILENAME=$DATADIR/webcam-`date +%s`.jpg
  fswebcam -r 960x540 --skip 2 --jpeg 70 - | \
    # openssl smime -encrypt -binary -aes-256-cbc -outform DER public-key.pem | \
    tee $FILENAME >/dev/null 2>&1
  echo "File written: $FILENAME"
  sleep $INTERVAL
done

