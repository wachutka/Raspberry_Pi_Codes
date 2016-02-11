'''
pi_rig contrains basic functions for using the raspberry pi behavior and electrophysiology rig in the Katz Lab

These functions can be used directly via ipython in a terminal window or called by other codes
'''

# Import things for running pi codes
import time
from math import floor
import random
import RPi.GPIO as GPIO

# Import things for data logging
import xlwt
import xlrd
from xlutils.copy import copy
import datetime
import os.path

# Setup pi board
GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

# To empty taste lines
def clearout(outports = [31, 33, 35, 37], dur = 5):

        # Setup pi board GPIO ports
	GPIO.setmode(GPIO.BOARD)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)

	for i in outports:
		GPIO.output(i, 1)
	time.sleep(dur)
	for i in outports:
		GPIO.output(i, 0)

	print('Tastant line clearing complete.')
	
	
# To calibrate taste lines
def calibrate(outports = [31, 33, 35, 37], opentime = 0.015, repeats = 5):

        # Setup pi board GPIO ports
	GPIO.setmode(GPIO.BOARD)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)

        # Open ports  
	for rep in range(repeats):
		for i in outports:
			GPIO.output(i, 1)
		time.sleep(opentime)
		for i in outports:
			GPIO.output(i, 0)
		time.sleep(3)

	print('Calibration procedure complete.')
	
	
# Passive H2O deliveries
def passive(outports = [31], opentimes = [0.01], iti = 15, trials = 150):

        # Setup pi board GPIO ports
	GPIO.setmode(GPIO.BOARD)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)

        # Set and radomize trial order
        tot_trials = len(outports) * trials
        count = 0
        trial_array = trials * range(len(outports))
        shuffle(trial_array)

	time.sleep(15)
	
	# Loop through trials
	for i in trial_array:
		GPIO.output(outports[i], 1)
		time.sleep(opentimes[i])
		GPIO.output(outports[i], 0)
		count += 1
		print('Trial '+str(count)+' of '+str(tot_trials)+' completed.')
		time.sleep(iti)

	print('Passive deliveries completed')
	

# Basic nose poking procedure to train poking for discrimination 2-AFC task
def basic_np(outport = 31, opentime = 0.012, iti = [.4, 1, 2], trials = 200, outtime = 0):

	intaninput = 5
	trial = 1
	inport = 13
	pokelight = 38
	houselight = 18
	lights = 0
	maxtime = 60

        # Setup pi board GPIO ports 
        GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pokelight, GPIO.OUT)
	GPIO.setup(houselight, GPIO.OUT)
	GPIO.setup(inport, GPIO.IN)
	GPIO.setup(outport, GPIO.OUT)
	GPIO.setup(intaninput, GPIO.OUT)
	
	time.sleep(15)
	starttime = time.time()

	while trial <= trials:

                # Timer to stop experiment if over 60 mins
		curtime = time.time()
		elapsedtime = round((curtime - starttime)/60, 2)
		if elapsedtime > maxtime:
			GPIO.output(pokelight, 0)
			GPIO.output(houselight, 0)
			break

		if lights == 0:
			GPIO.output(pokelight, 1)
			GPIO.output(houselight, 1)
			lights = 1

                # Check for pokes
		if GPIO.input(inport) == 0:
			poketime = time.time()
			curtime = poketime

                        # Make rat remove nose from nose poke to receive reward
			while (curtime - poketime) <= outtime:
				if GPIO.input(inport) == 0:
					poketime = time.time()
				curtime = time.time()

                        # Taste delivery and switch off lights
			GPIO.output(outport, 1)
			GPIO.output(intaninput, 1)
			time.sleep(opentime)
			GPIO.output(outport, 0)
			GPIO.output(intaninput, 1)
			GPIO.output(pokelight, 0)
			GPIO.output(houselight, 0)
			print('Trial '+str(trial)+' of '+str(trials)+' completed.')
			trial += 1
			lights = 0

                        # Calculate and execute ITI delay.  Pokes during ITI reset ITI timer.
			if trial <= trials/2:
				delay = floor((random.random()*(iti[1]-iti[0]))*100)/100+iti[0]
			else:
				delay = floor((random.random()*(iti[2]-iti[0]))*100)/100+iti[0]
	
			poketime = time.time()
			curtime = poketime

			while (curtime - poketime) <= delay:
				if GPIO.input(inport) == 0:
					poketime = time.time()
				curtime = time.time()
		
	print('Basic nose poking has been completed.')
	
	
# Clear all pi board GPIO settings
def clearall():
    
        # Pi ports to be cleared
	outports = [31, 33, 35, 37]
	inports = [11, 13, 15]
	pokelights = [36, 38, 40]
	houselight = 18
	lasers = [12, 22, 16]
	intan = [5, 7, 19, 21]
	
	# Set all ports to default/low state
	for i in intan:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, 0)
	
	for i in outports:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, 0)
		
	for i in inports:
		GPIO.setup(i, GPIO.IN, GPIO.PUD_UP)
		
	for i in pokelights:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, 0)
		
	for i in lasers:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, 0)
		
	GPIO.setup(houselight, GPIO.OUT)
	GPIO.output(houselight, 0)
