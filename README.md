USAGE OF OPENSSL
================

Create a new key pair.

    $ openssl req -x509 -nodes -newkey rsa:2048 \
        -keyout private-key.pem -out public-key.pem

Encrypt an image file using the Public Key.

    $ openssl smime -encrypt -binary -aes-256-cbc \
        -in pic.jpg -out pic.jpg.enc -outform DER public-key.pem

Read an image file and pipe it to the encrypter, and pipe the encrypted
result to another script.

    $ cat pic.jpg | openssl smime -encrypt -binary -aes-256-cbc \
        -outform DER public-key.pem | tee pic.jpg.enc >/dev/null 2>&1

Pipe an image from the camera to the encrypter and pipe the result
to another script.

    $ fswebcam -r 1920x1080 --skip 20 --jpeg 80 - | openssl smime -encrypt \
        -binary -aes-256-cbc -outform DER public-key.pem | \
        tee pic.jpg.enc >/dev/null 2>&1

Decrypt the encryped file using the Private Key.

    $ openssl smime -decrypt -in pic.jpg.enc -binary -inform DEM \
        -inkey private-key.pem -out pic.jpg

Get a list of encrypted files from a directory, pipe them to the decrypter
and write the decrypted results back.

    $ for F in ./*.jpg.enc; do cat $F | openssl smime -decrypt -binary \
        -inform DEM -inkey private-key.pem | tee ${F%.enc} >/dev/null 2>&1


