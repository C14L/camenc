#!/bin/bash

IMGDIR="/home/pi/temp/raspicam"

while [ true ]; do 
  raspistill -w 1280 -h 960 -q 70 -o "$IMGDIR/`date +%s`.jpg"
  sleep 1
done

