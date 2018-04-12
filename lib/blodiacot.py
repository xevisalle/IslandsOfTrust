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

import os
import time
from random import randint

def createStandard(nodesNumber):
	os.system("docker run -it -d --name snode1 snode /bin/bash")
	os.system("docker exec -t snode1 /bitcoin-0.14.2/bin/bitcoind -regtest -daemon")	

	ip = os.popen("docker exec -t snode1 ifconfig | grep -o '172.17[^ ]*'").read()
        ipParsed = ip[:len(ip)-1]

	addresses = []	
	address = ""
	while not address: 
		command = "docker exec -t snode1 /bitcoin-0.14.2/bin/bitcoin-cli -regtest getaddressesbyaccount \"\" | grep -oP '\"\K[^\"]+'"
		address = os.popen(command).read()

	addresses.append(address[:len(address)-2])
	f = open('database/standardaddresses', 'a+')
        f.write(address[:len(address)-2])

	for i in range(2, int(nodesNumber) + 1):
		os.system("docker run -it -d --name snode" + str(i) + " snode /bin/bash")
		os.system("docker exec -t snode" + str(i) + " /bitcoin-0.14.2/bin/bitcoind -regtest -connect=" + ipParsed + " -daemon")
		
		address = ""
		while not address: 
			command = "docker exec -t snode" + str(i) + " /bitcoin-0.14.2/bin/bitcoin-cli -regtest getaddressesbyaccount \"\" | grep -oP '\"\K[^\"]+'"
        		address = os.popen(command).read()

        	addresses.append(address[:len(address)-2])
                f.write(address[:len(address)-2])

	os.system("docker run -it -d --name snodeUSER snode /bin/bash")
        os.system("docker exec -t snodeUSER /bitcoin-0.14.2/bin/bitcoind -regtest -connect=" + ipParsed + " -daemon")

	address = ""
	while not address: 
        	command = "docker exec -t snodeUSER /bitcoin-0.14.2/bin/bitcoin-cli -regtest getaddressesbyaccount \"\" | grep -oP '\"\K[^\"]+'"
        	address = os.popen(command).read()

        f.write(address[:len(address)-2])
        
	f.close()

	os.system("docker exec -t snodeUSER /bitcoin-0.14.2/bin/bitcoin-cli -regtest generate 101")
        time.sleep(5)

	while True:
		for i in range(1, int(nodesNumber) + 1):
			os.system("docker exec -t snode" + str(i) + " /bitcoin-0.14.2/bin/bitcoin-cli -regtest generate " + str(randint(30, 50)))	
			time.sleep(5)

		for i in range(1, int(nodesNumber) + 1):
			j = randint(0, len(addresses)-1)
			while(i == j+1):
				j = randint(0, len(addresses)-1)
			
                        os.system("docker exec -t snode" + str(i) + " /bitcoin-0.14.2/bin/bitcoin-cli -regtest sendtoaddress " + addresses[j] + " 1.00")
                        time.sleep(5)
			os.system("docker exec -t snode" + str(i) + " /bitcoin-0.14.2/bin/bitcoin-cli -regtest generate 1")	
			time.sleep(15)

	return 

def createObligation(nodesNumber):
        os.system("docker run -it -d --name onode1 onode /bin/bash")
        ip = os.popen("docker exec -t onode1 ifconfig | grep -o '172.17[^ ]*'").read()
        ipParsed = ip[:len(ip)-1]

        os.system("docker exec -t onode1 nohup multichaind ochain -daemon")

        command = "docker exec -t onode1 multichain-cli ochain getaddresses | grep -oP '\"\K1[^\"]+'"
        address = os.popen(command).read()
        f = open('database/obligationaddresses', 'a+')
        f.write(address)

	os.system("docker exec -t onode1 nohup multichain-cli ochain create stream ServiceProvider1 false")
	command = "docker exec -t onode1 multichain-cli ochain publish ServiceProvider1 wifiAccess 12121212121212"
        f2 = open('database/obligationids', 'a+')
        obId = os.popen(command).read()
        f2.write(obId.splitlines()[2] + "\n")
        f2.close()

	f2 = open('database/obligationids', 'a+')

        for i in range(2, int(nodesNumber) + 1):
                os.system("docker run -it -d --name onode" + str(i) + " onode /bin/bash")
                os.system("docker exec -t onode" + str(i) + " ./deleteChain.sh")
                os.system("docker exec -t onode" + str(i) + " nohup multichaind ochain@" + ipParsed + ":4260 -daemon")
		command = "docker exec -t onode" + str(i) + " multichain-cli ochain getaddresses | grep -oP '\"\K1[^\"]+'"
        	address = os.popen(command).read()
        	f.write(address)
		os.system("docker exec -t onode1 nohup multichain-cli ochain create stream ServiceProvider" + str(i) + " false")
		command = "docker exec -t onode1 multichain-cli ochain publish ServiceProvider" + str(i) + " wifiAccess 12121212121212"
		obId = os.popen(command).read()
		f2.write(obId.splitlines()[2] + "\n")
	
	f2.close()
	f.close()

        return

def deleteChain(nodesNumber, chainType):
	if (chainType == "s"):
		os.system("docker kill snodeUSER")
        	os.system("docker rm snodeUSER")

	for i in range(1, int(nodesNumber) + 1):
                os.system("docker kill " + chainType + "node" + str(i))
                os.system("docker rm " + chainType + "node" + str(i))

	os.system("rm database/standardaddresses")
        os.system("rm database/obligationaddresses")
        os.system("rm database/obligationids")
        os.system("rm database/obligation")
        os.system("rm database/standard")
        os.system("rm lib/blodiacot.pyc")
        os.system("rm lib/__init__.pyc")

	return

def getStandardBalances(nodesNumber):
	print ""
	balance = os.popen("docker exec -t snodeUSER /bitcoin-0.14.2/bin/bitcoin-cli -regtest getbalance").read()
	print "snodeUSER: " + balance[:len(balance)-1]
	for i in range(1, int(nodesNumber) + 1):
		balance = os.popen("docker exec -t snode" + str(i) + " /bitcoin-0.14.2/bin/bitcoin-cli -regtest getbalance").read()
		print "snode" + str(i) + ": " + balance[:len(balance)-1]
	print ""

	return
