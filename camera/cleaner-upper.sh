#!/bin/bash

# Delete older local images from local SSD.

EXECDIR=/home/pi/dev/camenc
DATADIR=/home/pi/temp/raspicam
INTERVAL=60
MAXAGE=1440  # Maximum photo file age in minutes.

while [ true ]; do
  find $DATADIR -name "*.jpg.enc" -mmin +$MAXAGE -print0 | xargs -0 rm

  sleep $INTERVAL
done

