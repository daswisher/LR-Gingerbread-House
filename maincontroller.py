#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF, 0x9400D3]

pins = {'redPin':26, 'greenPin':19, 'bluePin':13}

#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for i in pins:
	print i, pins[i]
	GPIO.setup(pins[i], GPIO.OUT)
	GPIO.output(pins[i], GPIO.HIGH)

redPin = GPIO.PWM(pins['redPin'], 2000)
greenPin = GPIO.PWM(pins['greenPin'], 2000)
bluePin = GPIO.PWM(pins['bluePin'], 2000)
redPin.start(0)
greenPin.start(0)
bluePin.start(0)

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col):
	redVal = (col & 0x110000) >> 16
	blueVal = (col & 0x001100) >> 8
	greenVal = (col & 0x000011) >> 0

	redVal = map(redVal, 0, 255, 0, 255)
	blueVal = map(blueVal, 0, 255, 0, 255)
	greenVal = map(greenVal, 0, 255, 0, 255)
	print "redval", redVal
	print "blueval", blueVal
	print "greenval", greenVal

	#redPin.ChangeDutyCycle(100-redVal)
	#bluePin.ChangeDutyCycle(100-blueVal)
	#greenPin.ChangeDutyCycle(100-greenVal)

	redPin.ChangeDutyCycle(redVal)
	bluePin.ChangeDutyCycle(blueVal)
	greenPin.ChangeDutyCycle(greenVal)

try:
	while True:
		for col in colors:
			setColor(col)
			time.sleep(1.0)

except KeyboardInterrupt:
	redPin.stop()
	bluePin.stop()
	greenPin.stop()
	for i in pins:
		GPIO.output(pins[i], GPIO.HIGH)
	GPIO.cleanup()

