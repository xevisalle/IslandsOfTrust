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

from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError
import os

def createKeys():
	skSPB = SigningKey.generate(curve=SECP256k1)
	vkSPB = skSPB.get_verifying_key()
	open("database/SPBprivate.pem","w").write(skSPB.to_pem())
	open("database/SPBpublic.pem","w").write(vkSPB.to_pem())

	skSPD = SigningKey.generate(curve=SECP256k1)
        vkSPD = skSPD.get_verifying_key()
        open("database/SPDprivate.pem","w").write(skSPD.to_pem())
        open("database/SPDpublic.pem","w").write(vkSPD.to_pem())

	skSCB = SigningKey.generate(curve=SECP256k1)
        vkSCB = skSCB.get_verifying_key()
        open("database/SCBprivate.pem","w").write(skSCB.to_pem())
        open("database/SCBpublic.pem","w").write(vkSCB.to_pem())

	skSCD = SigningKey.generate(curve=SECP256k1)
        vkSCD = skSCD.get_verifying_key()
        open("database/SCDprivate.pem","w").write(skSCD.to_pem())
        open("database/SCDpublic.pem","w").write(vkSCD.to_pem())

	return

def createTx():
	# PROTOCOL STEP 0: SCD ASKS SPD FOR A SERVICE, AND SPD GETS THE OBLIGATION FROM SPB AND SEND THEM TO SCD
        obId = "ob123456789"
        terms = "I AM A SET OF TERMS."
        custData = "I AM CUSTOMER DATA."
	custReputationThreshold = 10

	SCBtoSign = obId + "_" + terms + "_" + custData

	os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
	skSCB = SigningKey.from_pem(open("database/SCBprivate.pem").read())
	SCBsig = skSCB.sign(SCBtoSign)
	SCBsigHex = SCBsig.encode('hex')

	# PROTOCOL STEP 1: SCD SENDS OBLIGATION SIGNED BY SCB TO SPD
	protocol1 = obId + "_" + terms + "_" + custData + "_" + SCBsigHex

	# PROTOCOL STEP 2: SPD ASKS SPB TO CHECK TERMS INTEGRITY
	termsChecking = ""
	i = 0
	while i < len(protocol1):
    		if (protocol1[i] == "_"):
			i += 1
			while (protocol1[i] != "_"):
    				termsChecking = termsChecking + protocol1[i]
				i += 1
			break
		i += 1

	if (termsChecking == terms):

		# PROTOCOL STEP 3: SPB CHECKS CUSTOMER REPUTATION
		os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
		custReputation = 15 #To be checked from reputation server
		if (custReputationThreshold < custReputation):
		
			# PROTOCOL STEP 4: SPB CHECKS IF TERMS SIGNATURE MATCHES
			receivedSCBsigHex = ""
			i += 1
        		while i < len(protocol1):
                		if (protocol1[i] == "_"):
                        		i += 1
                        		while (i < len(protocol1)):
                                		receivedSCBsigHex = receivedSCBsigHex + protocol1[i]
                                		i += 1
                        		break
                		i += 1
			
			receivedSCBsig = receivedSCBsigHex.decode("hex")
			os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
			vkSCB = VerifyingKey.from_pem(open("database/SCBpublic.pem").read())
			try:
    				vkSCB.verify(receivedSCBsig, SCBtoSign)

				# PROTOCOL STEP 5: SPB SIGNS THE OBLIGATION ALONG WITH AN ADDRESS AND SENDS IT BACK TO SPD
				os.system("docker exec -t snode1 /bitcoin-0.14.2/bin/bitcoin-cli -regtest getnewaddress")
				paymentAddress = "mJksieI94Jhsh4hFgN784Bc00233HjhdS" #To be created in bitcoin-core
				SPBtoSign = protocol1 + "_" + paymentAddress
				os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
				skSPB = SigningKey.from_pem(open("database/SPBprivate.pem").read())
        			SPBsig = skSPB.sign(SPBtoSign)
        			SPBsigHex = SPBsig.encode('hex')
				protocol2 = SPBsigHex + "_" + SPBtoSign

				# PROTOCOL STEP 6: SPD SIGNS THE OBLIGATION AND SENDS IT BACK TO SCD
				SPDtoSign = protocol2
				os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
                                skSPD = SigningKey.from_pem(open("database/SPDprivate.pem").read())
                                SPDsig = skSPD.sign(SPDtoSign)
                                SPDsigHex = SPDsig.encode('hex')
                                protocol3 = SPDsigHex + "_" + SPDtoSign

				# PROTOCOL STEP 7: SCD CHECKS THE SPD SIGNATURE
				receivedSPDsigHex = ""
                        	i = 0
                        	while (protocol3[i] != "_"):
					receivedSPDsigHex = receivedSPDsigHex + protocol3[i]
					i += 1

                        	receivedSPDsig = receivedSPDsigHex.decode("hex")
				os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
                        	vkSPD = VerifyingKey.from_pem(open("database/SPDpublic.pem").read())
				try:
                                	vkSPD.verify(receivedSPDsig, SPDtoSign)
					
					# PROTOCOL STEP 8: SCD SIGNS THE OBLIGATION
					SCDtoSign = protocol3
					os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
					skSCD = SigningKey.from_pem(open("database/SCDprivate.pem").read())
					SCDsig = skSCD.sign(SCDtoSign)
					SCDsigHex = SCDsig.encode('hex')
                                	protocol4 = SCDsigHex + "_" + SCDtoSign

					# PROTOCOL STEP 9: SPD VERIFIES SCD SIGNATURE AND GRANTS ACCESS TO THE SERVICE IF IT IS CORRECT (AND PUBLISHES THE TX)
					receivedSCDsigHex = ""
                                	i = 0
                                	while (protocol4[i] != "_"):
                                        	receivedSCDsigHex = receivedSCDsigHex + protocol4[i]
                                        	i += 1

                                	receivedSCDsig = receivedSCDsigHex.decode("hex")
					os.system("sqlite3 base100000 'select * from test where col=\"thisisatest\"'")
                                	vkSCD = VerifyingKey.from_pem(open("database/SCDpublic.pem").read())
                                	try:
                                        	vkSCD.verify(receivedSCDsig, SCDtoSign)
	                                        # PROTOCOL ENDS HERE
						os.system("docker exec -t onode1 multichain-cli ochain publish ServiceProvider1 id1212 1212")
                                                print "FINAL, all good."

					except BadSignatureError:
                                        	print "This never will happen."				

				except BadSignatureError:
                                	print "This never will happen."

			except BadSignatureError:
    				print "This never will happen."

	return
