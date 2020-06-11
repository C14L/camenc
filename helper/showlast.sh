#!/bin/bash

cat /WD1TB/camenc/$(ls /WD1TB/camenc/ | tail -n1) | \
  openssl smime -decrypt -binary -inform DEM -inkey private-key.pem | \
  feh -

