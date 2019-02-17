#!/bin/bash

SRC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DST="pi@192.168.0.206:/home/pi/dev/"

echo "${SRC} >>> ${DST}"
read -rsp "Press [ENTER] to start..."

rsync -rtvP --exclude=.git/ --exclude=.gitignore ${SRC} ${DST}

echo "Done."
echo
