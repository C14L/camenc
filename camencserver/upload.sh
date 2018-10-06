#!/bin/bash

# The directory of the upload.sh script
SRC=$( cd "$( dirname "$0" )"; pwd )

# The destination server and directory
DST="cst@89.110.147.123:/opt/"

echo "${SRC} >>> ${DST}"
read -rsp "Press [ENTER] to start..."

#find ${SRC} -type d -print0 | xargs -0 chmod 755
#find ${SRC} -type f -print0 | xargs -0 chmod 644
#chmod -R 755 ${SRC}/*.sh

rsync -rtvP \
    --delete \
    --exclude=__pycache__ \
    --exclude=*.swp \
    ${SRC} \
    ${DST}

