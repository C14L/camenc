#!/bin/bash

JPGFILE=$1

cat $JPGFILE.gpg | gpg --batch --passphrase 1234 --decrypt - > $JPGFILE

