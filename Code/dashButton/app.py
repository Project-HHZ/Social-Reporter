import time
import zmq
import logging
import datetime


#Declare&init vars
port = "45157"
now = datetime.datetime.now()
scriptPath = "/home/pi/IoT/dashButton/"

#Init logging
logging.basicConfig(filename=scriptPath+'dashButton.log',level=logging.DEBUG)

logging.debug("##################"+str(now)+"###################")
logging.debug("DashButton TP pressed")

#Init connection
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

socket.send ("SRCaptureImage#dashButton")
#  Get the reply.
message = socket.recv()
print "Received reply ", message
logging.debug("Received reply "+message+".")









