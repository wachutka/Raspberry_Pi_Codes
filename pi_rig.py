# Pi_Rig tasks for Blech Lab

import time
from math import floor
import random
import RPi.GPIO as GPIO

# For data logging
import xlwt
import xlrd
from xlutils.copy import copy
import datetime
import os.path

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
		time.sleep(3)

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
def basic_np(outport = 31, intaninput = 5, opentime = 0.012, iti = [.4, 1, 2], trials = 200, outtime = 0):

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
def multi_np(outports = [31, 37], inport = 13, opentimes = [0.1, .1], iti = [3, 4], rat = 'JW41'):

	GPIO.setmode(GPIO.BOARD)
	outtime = 0.1
	trial = 1
	block = 1
	maxtime = 5
	intermission = 1
	pokeside = []
	houselight = 18
	pokelight = 38
	intaninputs = [5, 7]
	pokecounter = [0, 0]
	taste = ['a', 'b']
	savefile = 'mixture_data'
	
	
	GPIO.setup(pokelight, GPIO.OUT)
	GPIO.setup(inport, GPIO.IN)
	for i in outports:
		GPIO.setup(i, GPIO.OUT)
	for i in intaninputs:
		GPIO.setup(i, GPIO.OUT)
	GPIO.setup(houselight, GPIO.OUT)
	
	time.sleep(15)

	#Start experiment
        for i in range(len(outports)):
		GPIO.output(pokelight, 1)
		GPIO.output(houselight, 1)
		starttime = time.time()
		curtime = time.time()
		elapsedtime = round((curtime - starttime)/60, 2)

		while elapsedtime <= maxtime:
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
		 		GPIO.output(outports[i], 1)
		 		GPIO.output(intaninputs[i], 1)
		 		time.sleep(opentimes[i])
		 		GPIO.output(outports[i], 0)
		 		GPIO.output(intaninputs[i], 0)
		 		pokecounter[i] += 1
		 			
		 		print('Poke! '+str(elapsedtime)+' minutes elapsed. Poke counter: '+str(pokecounter))
		 		delay = floor((random.random()*(iti[1]-iti[0]))*100)/100+iti[0]
		 		time.sleep(delay)
	   	        curtime = time.time()
	   	        elapsedtime = round((curtime - starttime)/60, 2)

		if i == 0:
		        GPIO.output(houselight, 0)
			GPIO.output(pokelight, 0)
			print('Begin 1 minute intermission. Beverages and snacks are available for purchase in the lobby.')
			time.sleep(intermission * 60)
			print('End of intermission; please resume regularly scheduled poking.')
			starttime = time.time()
			curtime = time.time()
	   	        elapsedtime = round((curtime - starttime)/60, 2)
			GPIO.output(pokelight, 1)
			GPIO.output(houselight, 1)

	GPIO.output(houselight, 0)
	GPIO.output(pokelight, 0)

	print('Nose poking preference task has been completed. Thank you for your participation!')

''' 	
	d = datetime.date.today()
        bold = xlwt.easyxf('font: bold 1')

	#Check for current data log
	if os.path.isfile('joe_data/'+str(savefile)):
	    dataold = xlrd.open_workbook('joe_data/'+str(savefile),formatting_info=True)
	    book = copy(dataold)
	    if rat in dataold.sheet_names():
		sheet1 = dataold.sheet_by_name(rat)
		currow = sheet1.nrows
	    else:
		sheet1 = book.add_sheet(rat)
		currow = 2
	    
	else:
	    book = xlwt.Workbook()
	    sheet1 = book.add_sheet(rat)
	    currow = 2
	    
	   #Create sheet and write file headings/structure
	    sheet1.write(0, 0, 'Date', bold)
	    sheet1.write(0, 1, 'Taste 1 Block 1', bold)
	    sheet1.write(0, 2, 'Taste 2 Block 1', bold)
	    sheet1.write(0, 3, 'Taste 1 Block 2', bold)
	    sheet1.write(0, 4, 'Taste 2 Block 2', bold)
	    
	    for i in range(len(b1ports)):
		if b1ports[i] == 31:
		    b1taste[i] = 'H2O'
		elif b1ports[i] == 33:
		    b1taste[i] = 'Sucrose'
		elif b1ports[i] >= 35:
		    b1taste[i] = 'NaCl'
		
	    for i in range(len(outports)):
		if outports[i] == 31:
		    taste[i] = 'H2O'
		elif outports[i] == 33:
		    taste[i] = 'Sucrose'
		elif outports[i] >= 35:
		    taste[i] = 'NaCl'
		    
	    for i in range(len(b1taste)):
		sheet1.write(1, i+1, b1taste[i])
	    for i in range(len(taste)):
		sheet1.write(1, i+3, taste[i])

		    
	# Write behavioral data to file

	sheet1.write(currow, 0, str('%02d' % d.year)+str('%02d' % d.month)+str('%02d' % d.day))

	for i in range(len(b1pokes)):
	    sheet1.write(currow, i+1, b1pokes[i])
	    
	for i in range(len(pokecounter)):
	    sheet1.write(currow, i+3, pokecounter[i])
	    
	#Save data file
	book.save('joe_data/'+str(savefile))
'''
		
	



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

	
