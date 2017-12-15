#!/usr/bin/env python

from pygame import mixer

import RPi.GPIO as GPIO
import threading
import signal
import time
import sys

###################################################
# Setup
###################################################

# Board setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED setup
colors = [0x00FFFF, 0xFF00FF, 0xFFFFFF]

############## GPIO 20 is broken on my personal board ##############
configuredLines = {
	'line1':{'redPinNum':13, 'greenPinNum':19, 'bluePinNum':26},
	'line2':{'redPinNum':16, 'greenPinNum':4, 'bluePinNum':21},
	'line3':{'redPinNum':17, 'greenPinNum':27, 'bluePinNum':22}
}

for ledLine in configuredLines:
	ledPins = configuredLines[ledLine]
	for i in ledPins:
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

# Audio setup
'''
mixer.init()
mixer.music.load('Get outta here.mp3')
mixer.music.play()
time.sleep(5)
mixer.stop()
#audioSound.set_volume(0.0)
'''

# Alarming status
alarmLock = threading.Lock()
colorIndex = 0

###################################################
# Classes
###################################################
class ledManager(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global colorIndex

		while True:
			# Iterate over all of the LED lines and set them to have different colors
			lineNumber = 0
			
			alarmLock.acquire()

			for lineName in sorted(configuredLines):
				lineColorIndex = (colorIndex + lineNumber) % len(colors)
				setColor(colors[lineColorIndex], configuredLines[lineName])
				lineNumber += 1

			colorIndex = (colorIndex + 1) % len(colors)
			alarmLock.release()
			time.sleep(3)

class sonarManager(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global colorIndex

		while True:
			# Check to see if there is something in front of the house and alarm if so
			if distance() < 100.0:
				alarmLock.acquire()

				# Alarm if there is something in front of the house
				for lineName in configuredLines:
					setColor(0xFF0000, configuredLines[lineName])

				while distance() < 100.0:
					time.sleep(0.5)

				lineNumber = 0

				for lineName in sorted(configuredLines):
					lineColorIndex = (colorIndex + lineNumber) % len(colors)
					setColor(colors[lineColorIndex], configuredLines[lineName])
					lineNumber += 1

				alarmLock.release()

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

	r_pin.ChangeDutyCycle(redVal)
	b_pin.ChangeDutyCycle(blueVal)
	g_pin.ChangeDutyCycle(greenVal)

def distance():
	GPIO.output(triggerPin, GPIO.LOW)

	# Let the sensor settle before sampling distance again
	time.sleep(0.01)

	GPIO.output(triggerPin, GPIO.HIGH)

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

	timeElapsed = StopTime - StartTime

	# Multiply with the sonic speed (34300 cm/s) and divide by 2, because there and back
	distance = (timeElapsed * 34300) / 2

	# Distance is in centimeters
	return distance

###################################################
# Main
###################################################

try:
	ledThread = ledManager()
	sonarThread = sonarManager()
	ledThread.daemon = True
	sonarThread.daemon = True
	ledThread.start()
	sonarThread.start()

	signal.pause()

except KeyboardInterrupt:
	print "Terminating: User halted script."
	sys.exit()

