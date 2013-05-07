from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN)
GPIO.setup(4, GPIO.IN)
GPIO.setup(17, GPIO.IN)

while True:
    if GPIO.input(22) == False:
        print "22 Pressed"
    if GPIO.input(4) == False:
        print "4 Pressed"
    if GPIO.input(17) == False:
        print "17 Pressed"
    sleep(0.1)
