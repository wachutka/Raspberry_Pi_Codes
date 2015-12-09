# Pi_Rig tasks for Blech Lab

# For Pi code
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


# Discrimination task training procedure
def disc_id(outports = [31, 33, 35, 37], opentimes = [0.05, 0.01, 0.07, 0.011, .175], iti = [8, 12, 12], trials = 200, blocksize = 10, trialdur = 10, blocked = 1, plswitch = 100, switchlights = 5, rat = 'JW43'):

	GPIO.setmode(GPIO.BOARD)
	startside = random.randint(0,1)
	outtime = 0.25
	trial = 0
	bothpl = 0			# bothpl = 1 for both lights, 0 for cue light only
	blcounter = 1
	lights = 0
	tarray = []
	taste = []
	pokeside = []
	correct = []
	pokelatency = []
	maxtime = 60


	bluecorrect = [0, 0, 0]
	greencorrect = [0]
	bluetrials = [0, 0, 0]
	greentrials = [0]
	nopoke = 0
	nopokecount = 0
	nopokepun = 10
	poke = 0
	


	inports = [11, 13, 15]
	pokelights = [36, 38, 40]
	houselight = 18
	intaninputs = [5, 7, 19, 21]
	
	for i in outports:
		GPIO.setup(i, GPIO.OUT)
	for i in intaninputs:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, 0)
	for i in inports:
		GPIO.setup(i, GPIO.IN, GPIO.PUD_UP)
	for i in pokelights:
		GPIO.setup(i, GPIO.OUT)
		GPIO.output(i, 0)
	GPIO.setup(houselight, GPIO.OUT)
	GPIO.output(houselight, 0)

	time.sleep(10)

	if blocked == 1:
		for i in range(trials):
			if i % blocksize == 0:
				blcounter += 1

			if blcounter % 2 == 0:
				if startside == 0:
					tarray.append(0)
				else:
					tarray.append(1)
			else:
				if startside == 0:
					tarray.append(1)
				else:
					tarray.append(0)	
	else:
		for i in range(trials):
			if i % 2 == 0:
				tarray.append(0)
			else:
				tarray.append(1)
		random.shuffle(tarray)	

	print(tarray)
	time.sleep(10)
	starttime = time.time()

	while trial < trials:
		curtime = time.time()
		elapsedtime = round((curtime - starttime)/60, 2)
		if elapsedtime > maxtime:
			break

		if lights == 0:
			GPIO.output(houselight, 1)
			GPIO.output(pokelights[1], 1)
			if blocked == 1:
				if trial % blocksize > (switchlights-1) or trial >= plswitch:
					bothpl = 1
				else:
					bothpl = 0
			else:
				if trial >= plswitch:
					bothpl = 1
				else:
					bothpl = 0
			if tarray[trial] == 0:
				print('This trial will be LEFT side (G). '+str(elapsedtime)+' mins elapsed.')
			else:
				print('This trial will be RIGHT side (B). '+str(elapsedtime)+' mins elapsed.')
			lights = 1	

# Check for pokes
		if GPIO.input(inports[1]) == 0:
			poketime = time.time()
			curtime = poketime

# Make rat remove nose from nose poke to receive reward
			while (curtime - poketime) <= outtime:
				if GPIO.input(inports[1]) == 0:
					poketime = time.time()
				curtime = time.time()
			
# Deliver cue taste and manipulate cue lights (depends on setting for bothpl)
			if tarray[trial] == 0:
				j = random.randint(0,1)		# Random choice for 'other' taste
				if j == 0:
					j2 = 2
					taste.append(j2)
				else:
					j2 = 3
					taste.append(j2)
				bluetrials[j] += 1
				GPIO.output(outports[j2], 1)
				GPIO.output(intaninputs[j2], 1)
				time.sleep(opentimes[j2])
				GPIO.output(outports[j2], 0)
				GPIO.output(intaninputs[j2], 0)
				GPIO.output(pokelights[1], 0)
				GPIO.output(houselight, 0)
				if bothpl == 0:
					GPIO.output(pokelights[0], 1)
				else:
					GPIO.output(pokelights[0], 1)
					GPIO.output(pokelights[2], 1)
# Wait for response poke and provide reward or timeout punishment
				timestart = time.time()
				curtime = timestart
				while (curtime - timestart) <= trialdur:
					if GPIO.input(inports[0]) == 0:
					        resptime = time.time()
					        triallat = resptime - timestart
						GPIO.output(pokelights[0], 0)
						GPIO.output(pokelights[2], 0)
						GPIO.output(outports[1], 1)
						GPIO.output(intaninputs[1], 1)
						time.sleep(opentimes[4])
						GPIO.output(outports[1], 0)
						GPIO.output(intaninputs[1], 0)
						poke = 1
						nopokecount = 0
						trial += 1
						bluecorrect[j] += 1
						pokeside.append('right')
						correct.append(1)
						pokelatency.append(triallat)
						break
					elif GPIO.input(inports[2]) == 0:
					        resptime = time.time()
					        triallat = resptime - timestart
						poke = 1
						if blocked == 0:
							trial += 1
						nopokecount = 0
						GPIO.output(pokelights[0], 0)
						GPIO.output(pokelights[2], 0)
						pokeside.append('left')
						correct.append(0)
						pokelatency.append(triallat)
						time.sleep(10)
						break
					curtime = time.time()
# Deliver cue taste and manipulate cue lights (depends on setting for bothpl)	
			else:
				k = 0
				taste.append(k)		
				greentrials[k] += 1
				GPIO.output(outports[k], 1)
				GPIO.output(intaninputs[k], 1)
				time.sleep(opentimes[k])
				GPIO.output(outports[k], 0)
				GPIO.output(intaninputs[k], 0)
				GPIO.output(pokelights[1], 0)
				GPIO.output(houselight, 0)
				if bothpl == 0:
					GPIO.output(pokelights[2], 1)
				else:
					GPIO.output(pokelights[0], 1)
					GPIO.output(pokelights[2], 1)

# Wait for response poke and provide reward or timeout punishment
				timestart = time.time()
				curtime = timestart
				while (curtime - timestart) <= trialdur:
					if GPIO.input(inports[2]) == 0:
					        resptime = time.time()
					        triallat = resptime - timestart
						GPIO.output(pokelights[0], 0)
						GPIO.output(pokelights[2], 0)
						GPIO.output(outports[1], 1)
						GPIO.output(intaninputs[1], 1)
						time.sleep(opentimes[4])
						GPIO.output(outports[1], 0)
						GPIO.output(intaninputs[1], 0)
						poke = 1
						nopokecount = 0
						trial += 1
						greencorrect[k] += 1
						pokeside.append('left')
						correct.append(1)
						pokelatency.append(triallat)
						break
					elif GPIO.input(inports[0]) == 0:
					        resptime = time.time()
					        triallat = resptime - timestart
						poke = 1
						if blocked == 0:
							trial += 1
						nopokecount = 0
						GPIO.output(pokelights[0], 0)
						GPIO.output(pokelights[2], 0)
						pokeside.append('right')
						correct.append(0)
						pokelatency.append(triallat)
						time.sleep(10)
						break
					curtime = time.time()
			totalcorrect = bluecorrect[0] + bluecorrect[1] + greencorrect[0] + bluecorrect[2]
			totaltrials = bluetrials[0] + bluetrials[1] + greentrials[0] + bluetrials[2]

			if poke == 0:
				nopoke += 1
				nopokecount += 1
				GPIO.output(pokelights[0], 0)
				GPIO.output(pokelights[2], 0)
				print('Last trial had no poke ('+str(nopoke)+' no poke trials). '+str(totalcorrect)+' of '+str(totaltrials)+' correct trials thus far.')
				nopokepun = nopokecount * 10
				time.sleep(nopokepun)
			else:
				print(str(totalcorrect)+' of '+str(totaltrials)+' correct trials thus far.')
			
			poke = 0
			lights = 0

# Calculate and execute ITI delay.  Pokes during ITI reset ITI timer.
			if trial <= trials/2:
				delay = floor((random.random()*(iti[1]-iti[0]))*100)/100+iti[0]
			else:
				delay = floor((random.random()*(iti[2]-iti[0]))*100)/100+iti[0]
			poketime = time.time()
			curtime = poketime
			while (curtime - poketime) <= delay:
				if GPIO.input(inports[1]) == 0:
					poketime = time.time()
				curtime = time.time()

# Turn off all lights and end procedure 
	GPIO.output(houselight, 0)
	for i in pokelights:
		GPIO.output(i, 0)
	
        d = datetime.date.today()
        bold = xlwt.easyxf('font: bold 1')

#Check for current data log
        if os.path.isfile('joe_data/'+str(rat)):
            dataold = xlrd.open_workbook('joe_data/'+str(rat),formatting_info=True)
            book = copy(dataold)

    
        else:
            book = xlwt.Workbook()
    
#Create sheet and write file headings/structure
        sheet1 = book.add_sheet(str('%02d' % d.year)+str('%02d' % d.month)+str('%02d' % d.day))
        sheet1.write(0, 0, 'Taste', bold)
        sheet1.write(0, 1, 'Side', bold)
        sheet1.write(0, 2, 'Correct', bold)
        sheet1.write(0, 3, 'Latency (ms)', bold)
        sheet1.write(0, 5, 'Total', bold)
        sheet1.write(0, 6, 'Correct', bold)
        sheet1.write(1, 5, xlwt.Formula('COUNT(C2:C300)'))
        sheet1.write(1, 6, xlwt.Formula('SUM(C2:C300)'))

#Write behavioral data to file
        for i in range(len(taste)):
            sheet1.write(i+1, 0, taste[i])
            
        for i in range(len(pokeside)):
            sheet1.write(i+1, 1, pokeside[i])
            
        for i in range(len(correct)):
            sheet1.write(i+1, 2, correct[i])
    
        for i in range(len(pokelatency)):
            pokelatency[i] = int(round(pokelatency[i]*10))
            sheet1.write(i+1, 3, pokelatency[i])

#Save data file
        book.save('joe_data/'+str(rat))
        
	print('Discrimination task is complete! Stats: '+str(bluecorrect[0])+'/'+str(bluetrials[0])+' Sacc trials correct, '+str(bluecorrect[1])+'/'+str(bluetrials[1])+' QHCl trials correct, '+str(greencorrect[0])+'/'+str(greentrials[0])+' CA trials correct, '+str(bluecorrect[2])+'/'+str(bluetrials[2])+' Suc trials correct, and '+str(nopoke)+' no poke trials.')


