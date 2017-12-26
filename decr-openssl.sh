#!/bin/bash

DATADIR=$1

echo "Extracting image in: $DATADIR ..."

for FILENAME in $DATADIR/*.jpg.enc; do
  cat $FILENAME | \
    openssl smime -decrypt -binary -inform DEM -inkey private-key.pem | \
    tee ${FILENAME%.enc} >/dev/null 2>&1
  echo "File extracted to: ${FILENAME%.enc}"
done

