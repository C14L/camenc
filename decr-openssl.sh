#!/bin/bash

BASEDIR=$(dirname "$0")
FILES=$1

echo "Extracting image in: $DATADIR ..."

for FILENAME in $FILES; do
  cat $FILENAME | \
    openssl smime -decrypt -binary -inform DEM -inkey "$BASEDIR/private-key.pem" | \
    tee ${FILENAME%.enc} >/dev/null 2>&1
  echo "File extracted to: ${FILENAME%.enc}"
done

