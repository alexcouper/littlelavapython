#!/usr/bin/env python

import RPi.GPIO as GPIO

DEBUG = 1

CYCLE_FREQ = 1

GPIO.setmode(GPIO.BCM)
LEDS = [18, 23, 25]
for led in LEDS:
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(led, False)
