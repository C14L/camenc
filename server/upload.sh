#!/bin/bash

SRC=$( cd "$( dirname "$0" )"; pwd )

SVR="chris@5.9.58.2"
DST="$SVR:/opt/camenc/"

echo "${SRC} >>> ${DST}"
rsync -rtvP --delete --exclude=*.log --exclude=db.sqlite3 ${SRC} ${DST}

#pass webdev/server01-chris | head -n1 | ssh -tt ${SVR} \
#    "sudo supervisorctl restart camencserver && sudo systemctl restart nginx"

