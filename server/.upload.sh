#!/bin/bash

[ -z "$SERVER01" ] && echo "Error: SERVER01 envvar not set." && exit 1

SRC=$( cd "$( dirname "$0" )"; pwd )
DST="$SERVER01:/opt/camenc/"

echo "${SRC} >>> ${DST}"
rsync -rtvP --delete --exclude=*.log --exclude=db.sqlite3 --exclude=**/__pycache__ ${SRC} ${DST}

pass webdev/server01-chris | head -n1 | ssh -tt ${SERVER01} "sudo systemctl restart camenc.service"
