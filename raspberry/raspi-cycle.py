#!/usr/bin/env python

import RPi.GPIO as GPIO, time

DEBUG = 1

CYCLE_FREQ = 1

GPIO.setmode(GPIO.BCM)
GREEN_LED = 18
RED_LED = 23
BLUE_LED = 25
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BLUE_LED, GPIO.OUT)

state = 0
states = [BLUE_LED, RED_LED, GREEN_LED]


def cycle():
    global state, states
    GPIO.output(GREEN_LED, states[state] == GREEN_LED)
    GPIO.output(RED_LED, states[state] == RED_LED)
    GPIO.output(BLUE_LED, states[state] == BLUE_LED)
    state = (state + 1) % 3


while True:
    cycle()
    time.sleep(CYCLE_FREQ)
