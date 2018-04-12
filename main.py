# -*- coding: utf-8 -*-

############################################################################
# 									   #
# SACMAT 2018 - A blockchain-based Trust System for the Internet of Things #
# 									   #
# Authors:								   #
# Roberto Di Pietro - HBKU-CSE - rdipietro@hbku.edu.qa			   #
# Xavier Salleras - UPF - xavier.salleras@upf.edu			   #
# Matteo Signorini - Nokia Bell Labs - matteo.signorini@nokia.com	   #
# Erez Waisbard - Nokia Bell Labs - erez.waisbard@nokia.com		   #
#									   #
############################################################################

import sys
from subprocess import Popen
from lib import blodiacot, signatures
from time import sleep
import os

def main():
	if (len(sys.argv) < 2):
		print "\nUSAGE:\n"
		print "sudo python main.py [OPTION] [arg]\n"
		print "Where 'a' means:"
		print "-s : Create and populate standard blockchain of [arg] nodes."
		print "-o : Create and populate obligation blockchain of [arg] nodes."
		print "-d : Delete standard and obligation chains."
		print "-b : Get balances of the standard nodes."
		print "-a : Retrieve standard addresses."
		print "-i : Retrieve obligation id's."
		print "-k : Create entities keys."
		print "-p : Perform the whole protocol to get a service."
                print ""

	else:
		if (sys.argv[1] == '-s'):
			nodes = sys.argv[2]
			f = open('database/standard', 'w')
			f.write(nodes)
			f.close()
			command = "nohup python -c 'from lib import blodiacot; blodiacot.createStandard(" + nodes + ")' > /dev/null 2>&1 &"
			Popen([command], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
			
			print "\nCreating blockchain...\n"
	
			items = list(range(1, int(nodes)))
			l = len(items)
			for i, item in enumerate(items):
    				while True:
    					if (os.popen("docker ps | grep -oP snode" + str(i+1)).read()):
						printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete...', length = 50)
						break

		if (sys.argv[1] == '-o'):
			nodes = sys.argv[2]
			f = open('database/obligation', 'w')
	                f.write(nodes)
			f.close()
			f2 = open('database/obligationids', 'w')
                        f2.write('')
                        f2.close()
			command = "nohup python -c 'from lib import blodiacot; blodiacot.createObligation(" + nodes + ")' > /dev/null 2>&1 &"
			Popen([command], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)		

			print "\nCreating blockchain...\n"

			items = list(range(1, int(nodes)))
                        l = len(items)
                        for i, item in enumerate(items):
                                while True:
					obIds = os.popen("cat database/obligationids").read()
                                        if (len(obIds.split('\n')) >= i+1):
                                                printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete...', length = 50)
                                                break

		if (sys.argv[1] == '-d'):
			f = open('database/standard', 'r')
			command = "nohup python -c 'from lib import blodiacot; blodiacot.deleteChain(" + f.read() + ", \"s\")' > /dev/null 2>&1 &"
			Popen([command], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
			f.close()
			f = open('database/obligation', 'r')
			command = "nohup python -c 'from lib import blodiacot; blodiacot.deleteChain(" + f.read() + ", \"o\")' > /dev/null 2>&1 &"
       		        Popen([command], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
			f.close()

		if (sys.argv[1] == '-b'):
			f = open('database/standard', 'r')
	                blodiacot.getStandardBalances(f.read())
			f.close()

		if (sys.argv[1] == '-a'):
			f = open('database/standard', 'r')
                        with open("database/standardaddresses", "r") as ins:
                                it = 1
				snodes = int(f.read())
                                print ""
                                for line in ins:
					if (snodes < it ):
						print "Address USER: " + line[:len(line)-1]
					else:
                                        	print "Address " + str(it) + ": " + line[:len(line)-1]
                                        it += 1
                                print ""

		if (sys.argv[1] == '-i'):
        	        with open("database/obligationids", "r") as ins:
				it = 1
				print ""	
    				for line in ins:
        				print "obligation ID " + str(it) + ": " + line[:len(line)-1]
					it += 1
				print ""

		if (sys.argv[1] == '-k'):
			signatures.createKeys()

		if (sys.argv[1] == '-p'):
			sleep(1)
			signatures.createTx()

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)

        sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
        sys.stdout.flush()

        if iteration == total:
                print " Done!\n"

main()
