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

############## GPIO 20 is broken on my personal board ##############
configuredLines = {
	'line1':{'redPinNum':13, 'greenPinNum':19, 'bluePinNum':26},
	'line2':{'redPinNum':16, 'greenPinNum':4, 'bluePinNum':21},
	'line3':{'redPinNum':17, 'greenPinNum':27, 'bluePinNum':22}
}

for ledLine in configuredLines:
	ledPins = configuredLines[ledLine]
	for i in ledPins:
		print i, ledPins[i]
		GPIO.setup(ledPins[i], GPIO.OUT)
		GPIO.output(ledPins[i], GPIO.HIGH)

	redPin = GPIO.PWM(ledPins['redPinNum'], 2000)
	greenPin = GPIO.PWM(ledPins['greenPinNum'], 2000)
	bluePin = GPIO.PWM(ledPins['bluePinNum'], 2000)
	redPin.start(0)
	greenPin.start(0)
	bluePin.start(0)

	configuredLines[ledLine]['redPin'] = redPin
	configuredLines[ledLine]['greenPin'] = greenPin
	configuredLines[ledLine]['bluePin'] = bluePin 

# Sonar sensor setup
echoPin = 5
triggerPin = 6
GPIO.setup(echoPin, GPIO.IN)
GPIO.setup(triggerPin, GPIO.OUT)

# Servo setup
dutyCycle = 7.5
servoPin = 12
GPIO.setup(servoPin, GPIO.OUT)

pwmServo = GPIO.PWM(servoPin, 50)
pwmServo.start(dutyCycle)

###################################################
# Functions
###################################################

def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(col, configuredLine):
	r_pin = configuredLine['redPin']
	b_pin = configuredLine['bluePin']
	g_pin = configuredLine['greenPin']
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

	r_pin.ChangeDutyCycle(redVal)
	b_pin.ChangeDutyCycle(blueVal)
	g_pin.ChangeDutyCycle(greenVal)

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
		StartTime = time.time()

	# Save time of arrival
	while GPIO.input(echoPin) == 1:
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

'''
try:
	while True:
		for col in colors:
			for lineName in configuredLines:
				setColor(col, configuredLines[lineName])
				time.sleep(1.0)

except KeyboardInterrupt:
	redPin.stop()
	bluePin.stop()
	greenPin.stop()
	for i in ledPins:
		GPIO.output(ledPins[i], GPIO.HIGH)
	GPIO.cleanup()

'''

'''
try:
	while True:
		dist = distance()
		print "Measured Distance = %.1f cm" % dist
		time.sleep(0.01)
except KeyboardInterrupt:
	print "Measurement stopped by user"
	GPIO.cleanup()

'''

try:
	while True:
		dutyCycle = float(input("Enter duty cycle; Left=5; Right = 10:"))
		pwmServo.ChangeDutyCycle(dutyCycle)
except KeyboardInterrupt:
	print "CTRL-C: Terminating program."
	GPIO.cleanup()
