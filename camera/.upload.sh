#!/bin/bash

[ -z "$RASPI01" ] && echo "Error: RASPI01 envvar not set." && exit 1

SRC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="/home/pi/camenc"
DST="${RASPI01}:${DIR}/"

echo "${SRC} >>> ${DST}"

ssh ${RASPI01} "mkdir -p ${DIR}"

rsync -rtvP --exclude=.git/ --exclude=.gitignore "${SRC}" "${DST}"

ssh ${RASPI01} "\
  sudo ln -s ${DIR}/camera/camenc-camera.service /etc/systemd/system/ 2>/dev/null ; \
  sudo ln -s ${DIR}/camera/camenc-cleanup.service /etc/systemd/system/ 2>/dev/null ; \
  sudo systemctl daemon-reload ; \
  sudo systemctl restart camenc-camera.service ; \
  sudo systemctl restart camenc-cleanup.service
"

