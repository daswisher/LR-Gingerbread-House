#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

###################################################
# Setup
###################################################

# Board setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED setup
colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xFFFFFF, 0x9400D3]

ledPins = {'redPin':26, 'greenPin':19, 'bluePin':13}


for i in ledPins:
	print i, ledPins[i]
	GPIO.setup(ledPins[i], GPIO.OUT)
	GPIO.output(ledPins[i], GPIO.HIGH)

redPin = GPIO.PWM(ledPins['redPin'], 2000)
greenPin = GPIO.PWM(ledPins['greenPin'], 2000)
bluePin = GPIO.PWM(ledPins['bluePin'], 2000)
redPin.start(0)
greenPin.start(0)
bluePin.start(0)

# Sonar sensor setup
echoPin = 20 #It's actually 20
triggerPin = 21 #It's actually 21
GPIO.setup(echoPin, GPIO.IN)
GPIO.setup(triggerPin, GPIO.OUT)

###################################################
# Functions
###################################################

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

def distance():
	GPIO.output(triggerPin, GPIO.LOW)
	time.sleep(1)

	# Set trigger to HIGH
	GPIO.output(triggerPin, GPIO.HIGH)

	# Set trigger after 0.01ms to LOW
	time.sleep(0.00001)
	GPIO.output(triggerPin, GPIO.LOW)
	
	StartTime = time.time()
	StopTime = time.time()

	# Save StartTime
	while GPIO.input(echoPin) == 0:
		print "echo low:", GPIO.input(echoPin)
		StartTime = time.time()

	# Save time of arrival
	while GPIO.input(echoPin) == 1:
		print "echo high:", GPIO.input(echoPin)
		StopTime = time.time()

	# Time difference between start and arrival
	timeElapsed = StopTime - StartTime

	# Multiply with the sonic speed (34300 cm/s)
	# and divide by 2, because there and back
	distance = (timeElapsed * 34300) / 2

	return distance

###################################################
# Main
###################################################

try:
	while True:
		for col in colors:
			setColor(col)
			time.sleep(1.0)

except KeyboardInterrupt:
	redPin.stop()
	bluePin.stop()
	greenPin.stop()
	for i in ledPins:
		GPIO.output(ledPins[i], GPIO.HIGH)
	GPIO.cleanup()

'''

try:
	while True:
		dist = distance()
		print "Measured Distance = %.1f cm" % dist
		time.sleep(1)
except KeyboardInterrupt:
	print "Measurement stopped by user"
	GPIO.cleanup()

'''
