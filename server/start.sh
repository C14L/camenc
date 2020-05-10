#!/bin/bash

NAME="camencserver_app"
USER=chris
GROUP=chris

DJANGODIR=/opt/camenc/server
DJANGO_SETTINGS_MODULE=camencserver.settings
DJANGO_WSGI_MODULE=camencserver.wsgi

SOCKFILE=/opt/camenc/run/gunicorn.sock
VENVDIR=/opt/venvs/camenc

echo "Starting gateway $NAME as $(whoami)..."

cd $DJANGODIR
source $VENVDIR/bin/activate
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
export PYTHONPATH=${DJANGODIR}:${PYTHONPATH}

RUNDIR=$(dirname ${SOCKFILE})
test -d ${RUNDIR} || mkdir -p ${RUNDIR}

NUM_WORKERS=1  # total workers, ~ 2-4 x number of cores
NUM_THREADS=4  # threads per worker, ~ 2-4 x number of cores

exec $VENVDIR/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name ${NAME} \
  --workers ${NUM_WORKERS} \
  --threads ${NUM_THREADS} \
  --user=${USER} \
  --group=${GROUP} \
  --bind=unix:${SOCKFILE} \
  --log-level=info \
  --log-file=-

echo "Gunicorn started."
