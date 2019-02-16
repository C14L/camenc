#!/usr/bin/python3

import RPi.GPIO as GPIO
import datetime
import logging
import time

log = logging.getLogger('raspi_doorman')
handler = logging.FileHandler('/tmp/raspi_doorman.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler) 
log.setLevel(logging.INFO)

# GPIO-Port to connect one side on the switch: GPIO 5 (Pin 29)
# The other side of the switch is connected to any ground (GND)
# pin (for example Pin 30 right next to Pin 29).
GPIO_SWITCH = 5

# GPIO-Port to connect the middle pin of the motion detector.
# This is GPIO 4 (Pin 7) on the Raspi. The motion detector's
# left and right side pins are connected to 5v (Pin 2) and to
# Ground (GND, Pin 6).
GPIO_PIR = 4

# State threshold. A state has to be stable for this many seconds
# before the new state is counted. If it flips back to the previous
# state within this threshold, the state flip is ignored.
THRESHOLD = 0.5

# Init GPIO, BMC-Pin number, and Pullup-Resistor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PIR, GPIO.IN)

# Initialize PIR, it has to be 0.
log.info("Initializing motion detector")
while GPIO.input(GPIO_PIR) != 0:
    time.sleep(0.1)
log.info("Motion detector ready")

# Initialize switch state and time.
switch_time = time.time()
door_state = 'OPEN' if GPIO.input(GPIO_SWITCH) else 'CLOSE'
log.info("Door is initially %s." % door_state)

# Callback for motion detector signal.
def motion_callback(pin):
    log.warning("Something moved!")

# Callback for switch signal.
def switch_callback(pin):
    global switch_time
    global door_state

    if GPIO.input(pin):
        if door_state == 'CLOSE':
            door_state = 'OPEN'
            elapsed = time.time() - switch_time
            switch_time = time.time()
            log.warning('Door OPENED after %.2f seconds.', elapsed)
    else:
        if door_state == 'OPEN':
            door_state = 'CLOSE'
            elapsed = time.time() - switch_time
            switch_time = time.time()
            log.warning('Door CLOSED after %.2f seconds.', elapsed)

# Interrupt for switch change signal
GPIO.add_event_detect(GPIO_SWITCH, GPIO.BOTH, callback=switch_callback)
GPIO.add_event_detect(GPIO_PIR, GPIO.RISING, callback=motion_callback)

try:
    while True:
        time.sleep(100)

except KeyboardInterrupt:
    log.info("Shutting down")
    GPIO.cleanup()

