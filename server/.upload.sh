#!/bin/bash

SRC=$( cd "$( dirname "$0" )"; pwd )

SVR="$SERVER01"
DST="$SVR:/opt/camenc/"

echo "${SRC} >>> ${DST}"
rsync -rtvP --delete --exclude=*.log --exclude=db.sqlite3 ${SRC} ${DST}

pass webdev/server01-chris | head -n1 | ssh -tt ${SVR} "sudo systemctl restart camenc.service"

