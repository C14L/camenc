#!/bin/bash

NAME="camencserver_app"
USER=cst
GROUP=cst

DJANGODIR=/opt/camencserver
DJANGO_SETTINGS_MODULE=camencserver.settings
DJANGO_WSGI_MODULE=camencserver.wsgi

SOCKFILE=/var/run/camencserver.sock

echo "Starting gateway $NAME as $(whoami)..."

cd $DJANGODIR
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}
export PYTHONPATH=${DJANGODIR}:${PYTHONPATH}

RUNDIR=$(dirname ${SOCKFILE})
test -d ${RUNDIR} || mkdir -p ${RUNDIR}

################################################################################
### DAPHNE #####################################################################
################################################################################

exec ${DJANGODIR}/../venv/bin/daphne dtr4.asgi:channel_layer -u=${SOCKFILE} &

exec python ${DJANGODIR}/manage.py runworker

################################################################################
### GUNICORN ###################################################################
################################################################################

#NUM_WORKERS=1  # total workers, ~ 2-4 x number of cores
#NUM_THREADS=4  # threads per worker, ~ 2-4 x number of cores
#
#exec ../venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
#  --name ${NAME} \
#  --workers ${NUM_WORKERS} \
#  --threads ${NUM_THREADS} \
#  --user=${USER} \
#  --group=${GROUP} \
#  --bind=unix:${SOCKFILE} \
#  --log-level=debug --log-file=-
#
#echo "Gunicorn started."
