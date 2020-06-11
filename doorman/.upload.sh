#!/bin/bash

[ -z "$RASPI03" ] && echo "Error: RASPI03 envvar not set." && exit 1

SRC="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="/home/pi/camenc"
DST="${RASPI03}:${DIR}/"

echo "${SRC} >>> ${DST}"

ssh ${RASPI03} "mkdir -p ${DIR}"

rsync -rtvP --exclude=.git/ --exclude=.gitignore ${SRC} ${DST}

ssh ${RASPI03} "\
  sudo ln -s ${DIR}/camera/camenc-doorman.service /etc/systemd/system/ 2>/dev/null ; \
  sudo systemctl restart camenc-doorman.service ; \
"

