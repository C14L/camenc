#!/usr/bin/python3

import RPi.GPIO as GPIO
from datetime import datetime as dt
import logging
import requests
import time

#url = 'http://192.168.0.136:8000/doorman/add'
url = 'https://c14l.com/doorman/add'

log_fname = '/tmp/doorman.%s.log' % dt.strftime(dt.now(), '%Y%m%dT%H%M%S')
log = logging.getLogger('doorman')
handler = logging.FileHandler(log_fname)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

log.setLevel(logging.WARNING)

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
SWITCH_TIME_THRESHOLD = 0.5

# The motion sensor only reports if within this time span it
# activated at least this many times.
MOTION_COUNT_TIMESPAN = 20  # seconds
MOTION_COUNT_THRESHOLD = 2

# Init GPIO, BMC-Pin number, and Pullup-Resistor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_PIR, GPIO.IN)

# Globals
last_motions = []
switch_time = None
door_state = None


def post(data):
    try:
        requests.post(url, {'data': data})
    except requests.exceptions.ConnectionError:
        _log.error('Data POST failed, with data: "%s"', data)


def init_motion_detector():
    # Initialize PIR, it has to be 0.
    log.info("Initializing motion detector")
    while GPIO.input(GPIO_PIR) != 0:
        time.sleep(0.1)
    log.info("Motion detector ready")


def init_door_switch():
    # Initialize switch state and time.
    global switch_time
    global door_state

    switch_time = time.time()
    door_state = 'OPEN' if GPIO.input(GPIO_SWITCH) else 'CLOSE'

    log.warning("Doorman starts to watch the door...")
    log.warning("Door is %s." % door_state)

    post('Startup: initial door state %s' % door_state)


# Callback for motion detector signal.
def motion_callback(pin):
    global last_motions

    signal = GPIO.input(pin)
    log.info('PIR signal: %s', signal)

    now = int(time.time())
    min_time = now - MOTION_COUNT_TIMESPAN
    last_motions = [x for x in last_motions if x > min_time]
    last_motions.append(now)
    cnt = len(last_motions)

    if cnt >= MOTION_COUNT_THRESHOLD:
        s = "Movement detected: %d in the past %d seconds."
        s = s % (cnt, MOTION_COUNT_TIMESPAN)
        log.warning(s)
        post(s)


# Callback for switch signal.
def switch_callback(pin):
    global switch_time
    global door_state

    if GPIO.input(pin):
        if door_state == 'CLOSE':
            door_state = 'OPEN'
            elapsed = time.time() - switch_time
            switch_time = time.time()
            s = 'Door OPENED after %.2f seconds.' % (elapsed,)
            log.warning(s)
            post(s)
    else:
        if door_state == 'OPEN':
            door_state = 'CLOSE'
            elapsed = time.time() - switch_time
            switch_time = time.time()
            s = 'Door CLOSED after %.2f seconds.' % (elapsed,)
            log.warning(s)
            post(s)


def run():
    init_motion_detector()
    init_door_switch()

    # Set callbacks for signal changes
    GPIO.add_event_detect(GPIO_SWITCH, GPIO.BOTH, callback=switch_callback)
    GPIO.add_event_detect(GPIO_PIR, GPIO.RISING, callback=motion_callback)

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        log.warning("Doorman shutting down!")
        post('Doorman shutting down!')
        GPIO.cleanup()


if __name__ == "__main__":
    run()
