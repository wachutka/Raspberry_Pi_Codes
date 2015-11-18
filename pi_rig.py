# Pi_Rig tasks for Blech Lab

import time
from math import floor
import random
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

# Clear tastant lines
def clearout(outports = [31, 33, 35, 37], dur = 5):

	GPIO.setmode(GPIO.BOARD)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)

	for i in outports:
		GPIO.output(i, 1)
	time.sleep(dur)
	for i in outports:
		GPIO.output(i, 0)

	print('Tastant line clearing complete.')

# Calibrate tastant lines
def calibrate(outports = [31, 33, 35, 37], opentime = 0.015, repeats = 5):

	GPIO.setmode(GPIO.BOARD)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)

	for rep in range(repeats):
		for i in outports:
			GPIO.output(i, 1)
		time.sleep(opentime)
		for i in outports:
			GPIO.output(i, 0)
		time.sleep(4)

	print('Calibration procedure complete.')

# Passive H2O deliveries
def passive(outport = 31, opentime = 0.01, iti = 15, trials = 150):

	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(outport, GPIO.OUT)

	time.sleep(10)
	
	for trial in range(trials):
		GPIO.output(outport, 1)
		time.sleep(opentime)
		GPIO.output(outport, 0)
		print('Trial '+str(trial+1)+' of '+str(trials)+' completed.')
		time.sleep(iti)

	print('Passive deliveries completed')

# Basic nose poking procedure for H2O rewards
def basic_np(outport = 31, intaninput = 5, opentime = 0.0125, iti = [.4, 1, 1.5], trials = 150, outtime = 0):

	GPIO.setmode(GPIO.BOARD)
	trial = 1
	inport = 13
	pokelight = 38
	houselight = 18
	lights = 0
	maxtime = 60

	GPIO.setup(pokelight, GPIO.OUT)
	GPIO.setup(houselight, GPIO.OUT)
	GPIO.setup(inport, GPIO.IN)
	GPIO.setup(outport, GPIO.OUT)
	GPIO.setup(intaninput, GPIO.OUT)
	

	time.sleep(5)
	starttime = time.time()

	while trial <= trials:

# Timer to stop experiment
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

# Passive delivery
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


# Multiple nose poke procedure for preference measurements 
def multi_np(outports = [31, 33, 35], inports = [11, 13, 15], pokelights = [36, 38, 40], opentimes = [0.011, .012, .011], iti = [1, 2], trials = 250):

	GPIO.setmode(GPIO.BOARD)
	outtime = 0.1
	trial = 1
	tarray = []
	houselight = 18
	pokecounter = [0, 0, 0]
	intaninputs = [5, 7, 19, 21]
	for i in pokelights:
		GPIO.setup(i, GPIO.OUT)
	GPIO.setup(houselight, GPIO.OUT)
	for i in inports:
		GPIO.setup(i, GPIO.IN)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)
	for i in intaninputs:
		GPIO.setup(i, GPIO.OUT)
	
	time.sleep(5)
	starttime = time.time()

	for i in pokelights:
		GPIO.output(i, 1)
	GPIO.output(houselight, 1)

	while trial <= trials:
# Check for pokes
		for i in range(len(inports)):
			if GPIO.input(inports[i]) == 0:
				poketime = time.time()
				curtime = poketime

# Make rat remove nose from nose poke to receive reward
				while (curtime - poketime) <= outtime:
					if GPIO.input(inports[i]) == 0:
						poketime = time.time()
					curtime = time.time()

# Stimulus delivery
				GPIO.output(outports[i], 1)
				GPIO.output(intaninputs[i], 1)
				time.sleep(opentimes[i])
				GPIO.output(outports[i], 0)
				GPIO.output(intaninputs[i], 0)
				pokecounter[i] += 1
				curtime = time.time()
				elapsedtime = round((curtime - starttime)/60, 2)
				print('Trial '+str(trial)+' of '+str(trials)+' completed. '+str(elapsedtime)+' minutes elapsed. Poke counter: '+str(pokecounter))
				trial += 1
				delay = floor((random.random()*(iti[1]-iti[0]))*100)/100+iti[0]
				time.sleep(delay)
		curtime = time.time()
		elapsedtime = round((curtime - starttime)/60, 2)
		if elapsedtime > 30:
			break
		
	for i in pokelights:
		GPIO.output(i, 0)
	GPIO.output(houselight, 0)
	print('Nose poking preference task has been completed. Total Time: '+str(elapsedtime)+' mins. Poke counter: '+str(pokecounter))

# Multiple nose poke procedure for preference measurements 
def multi_rand(outports = [33, 35], inport = 13, pokelight = 38, opentimes = [0.009, .009], iti = [3, 5]):

	GPIO.setmode(GPIO.BOARD)
	trials = 250
	outtime = 0.1
	trial = 1
	tarray = []
	houselight = 18
	pokecounter = [0, 0, 0]
	intaninputs = [7, 19]
	GPIO.setup(pokelight, GPIO.OUT)
	GPIO.setup(houselight, GPIO.OUT)
	GPIO.setup(inport, GPIO.IN)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)
	for i in intaninputs:
		GPIO.setup(i, GPIO.OUT)

	for i in range(trials):
		if i % 2 == 0:
			tarray.append(0)
		else:
			tarray.append(1)
	random.shuffle(tarray)	
	
	time.sleep(5)
	starttime = time.time()

	GPIO.output(pokelight, 1)
	GPIO.output(houselight, 1)

	while trial <= trials:

# Check for pokes
		if GPIO.input(inport) == 0:
			poketime = time.time()
			curtime = poketime

# Make rat remove nose from nose poke to receive reward
			while (curtime - poketime) <= outtime:
				if GPIO.input(inport) == 0:
					poketime = time.time()
				curtime = time.time()

# Stimulus delivery
			j = tarray[trial - 1]
			GPIO.output(outports[j], 1)
			GPIO.output(intaninputs[j], 1)
			time.sleep(opentimes[j])
			GPIO.output(outports[j], 0)
			GPIO.output(intaninputs[j], 0)
			pokecounter[j] += 1
			curtime = time.time()
			elapsedtime = round((curtime - starttime)/60, 2)
			print('Trial '+str(trial)+' of '+str(trials)+' completed. '+str(elapsedtime)+' minutes elapsed. Poke counter: '+str(pokecounter))
			trial += 1
			delay = floor((random.random()*(iti[1]-iti[0]))*100)/100+iti[0]
			time.sleep(delay)
		curtime = time.time()
		elapsedtime = round((curtime - starttime)/60, 2)
		if elapsedtime > 30:
			break
		

	GPIO.output(pokelight, 0)
	GPIO.output(houselight, 0)
	print('Nose poking preference task has been completed. Total Time: '+str(elapsedtime)+' mins. Poke counter: '+str(pokecounter))


# Clear all outputs from Pi
def clearall():
	outports = [31, 33, 35, 37]
	inports = [11, 13, 15]
	pokelights = [36, 38, 40]
	houselight = 18
	lasers = [12, 22, 16]
	intan = [5, 7, 19, 21]
	
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

	
