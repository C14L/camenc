CAMENC
======

Scripts to use Raspis for home surveillance.


Camera
------

Uses a Raspi Nano to take a picture every few seconds, encrypts it with a
public key, and uploads it to a server. On a second bash stream, it takes
the same picture and scales it down to thumbnail size and uploads it
unencrypted.


Doorman
-------

Uses a Raspi Nano and some sensors to detect an opened door, movement and
light. Posts current state changs to the server every second or so.


