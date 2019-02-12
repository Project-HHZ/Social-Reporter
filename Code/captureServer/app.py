import zmq
import time
import cv2
import logging
import datetime
import RPi.GPIO as GPIO
import os
import random

#Declare&init vars
NOW = datetime.datetime.now()
SCRIPT_PATH = "/home/pi/IoT/captureServer/"
IMAGE_PATH = "/home/pi/IoT/softButton/static/images/"
PORT = "45157"
RECORDING_STATUS = True
CURRENT_LECTURE = "notDefined"
DESCRIPTION_PATH = "/home/pi/IoT/description/"
MONTION_DETECTED = int(time.time())


#Init LEDs
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT)
GPIO.output(24,GPIO.HIGH)

#Init logging
logging.basicConfig(filename=SCRIPT_PATH+'captureServer.log',level=logging.DEBUG)

#Init Server
int(PORT)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % PORT)
print "Server listening on Port:"+PORT+"."
logging.debug("##################"+str(NOW)+"###################")
logging.debug("Server listening on Port:"+PORT+".")

#Improve video settings
os.system('/usr/bin/v4l2-ctl -d /dev/video0 -c exposure_auto=0 -c sharpness=128 --set-fmt-video=width=1920,height=720')

#Process incomming requests
while True:
    #  Wait for next request from client
    dataString = socket.recv()
    message = dataString.split("#")

    if message[0] == "SRCaptureImage" or message[0] == "SRStartStopRecording" or message[0] == "SRStopRecording" or message[0] == "SRStartRecording":
	    # Take picture
            if message[0] == "SRCaptureImage" and RECORDING_STATUS == True:
                t = str(time.time())
                print "["+t+"] Received request from: "+message[1]+" Task: Capture image"
                logging.debug("["+t+"] Received request from: "+message[1]+" Task: Capture image")

                if message[1] == "sensors": 
                   MONTION_DETECTED = int(time.time())
                   logging.debug("Motion detected...")
                   #notify sender
                   print "["+t+"] No Saved image for: "+message[1]+"."
                   logging.debug("["+t+"] No Saved image for: "+message[1]+".")
                   socket.send("No Image saved!")
                if (message[1] == "faceDetection" and (int(time.time()) - MONTION_DETECTED) <= 10) or message[1] == "dashButton":
                   #Init cam
                   time.sleep(2)
                   camera = cv2.VideoCapture(0)
                   image = camera.read()[1]
                   time.sleep(3)
                   image = camera.read()[1]
                   cv2.imwrite(SCRIPT_PATH+'pics/'+message[1]+'/'+CURRENT_LECTURE+'-'+str(datetime.datetime.now())+'.png', image)
                   logging.debug("Bild gespeichert unter: "+SCRIPT_PATH+'pics/'+message[1]+'/'+CURRENT_LECTURE+'-'+str(datetime.datetime.now())+'.png')
                   cv2.imwrite(IMAGE_PATH+'lastpic.png', image)
                   camera.release()
                   #Init text description
                   descriptions = open(DESCRIPTION_PATH+'descriptions.txt').read().splitlines()
                   description = random.choice(descriptions)
                   hashtags = open(DESCRIPTION_PATH+'hashtags.txt').read().splitlines()
                   hashtag = random.choice(hashtags)
                   output = description+" "+CURRENT_LECTURE+" "+hashtag
                   completeName = SCRIPT_PATH+'pics/'+message[1]+'/'+CURRENT_LECTURE+'-'+str(datetime.datetime.now())+'.txt'
                   logging.debug(completeName)
                   file1 = open(completeName, "w+")
                   file1.write(output)
                   file1.close()
                   #notify sender
                   print "["+t+"] Saved image for: "+message[1]+"."
                   logging.debug("["+t+"] Saved image for: "+message[1]+".")
                   socket.send("Image saved!")

            if message[0] == "SRCaptureImage" and RECORDING_STATUS == False:
                #notify sender
                print "["+t+"] Recording turned off: "+message[1]+"."
                logging.debug("["+t+"] Recording turned off: "+message[1]+".")
                socket.send("Recording turned off!")

	    # Start/Stop recording
	    if message[0] == "SRStartStopRecording":
	        t = str(time.time())
	        print "["+t+"] Received request from: "+message[1]+"."
	        logging.debug("["+t+"] Received request from: "+message[1]+".")
		if RECORDING_STATUS == False:
	        	GPIO.output(24,GPIO.HIGH)
                        RECORDING_STATUS = True
                        #notify sender
                        print "["+t+"] Recording started: "+message[1]+"."
	        	logging.debug("["+t+"] Recording started: "+message[1]+".")
        		socket.send("Recording started!")
		else:
        		RECORDING_STATUS = False
                        GPIO.output(24,GPIO.LOW)
	        	#notify sender
	        	print "["+t+"] Recording stopped: "+message[1]+"."
	        	logging.debug("["+t+"] Recording stopped: "+message[1]+".")
        		socket.send("Recording stopped!")

            # Stop recording
            if message[0] == "SRStopRecording":
                t = str(time.time())
                print "["+t+"] Received request from: "+message[1]+"."
                logging.debug("["+t+"] Received request from: "+message[1]+".")
                if RECORDING_STATUS == True:
                        RECORDING_STATUS = False
                        GPIO.output(24,GPIO.LOW)
                        #notify sender
                        print "["+t+"] Recording stopped: "+message[1]+"."
                        logging.debug("["+t+"] Recording stopped: "+message[1]+".")
                        socket.send("Recording stopped!")
                else:
                        #notify sender
                        print "["+t+"] Recording already stopped: "+message[1]+"."
                        logging.debug("["+t+"] Recording already stopped: "+message[1]+".")
                        socket.send("Recording already stopped!")

            # Start recording
            if message[0] == "SRStartRecording":
                t = str(time.time())
                print "["+t+"] Received request from: "+message[1]+" Current lecture: "+message[2]+"."
                logging.debug("["+t+"] Received request from: "+message[1]+" Current lecture: "+message[2])
                CURRENT_LECTURE = message[2]
                if RECORDING_STATUS == False:
                        GPIO.output(24,GPIO.HIGH)
                        RECORDING_STATUS = True
                        #notify sender
                        print "["+t+"] Recording started: "+message[1]+"."
                        logging.debug("["+t+"] Recording started: "+message[1]+".")
                        socket.send("Recording started!")
                else:
                        #notify sender
                        print "["+t+"] Recording already started: "+message[1]+"."
                        logging.debug("["+t+"] Recording already started: "+message[1]+".")
                        socket.send("Recording already started!")


    # Invalid request
    else:
            print "Received request not valid: "+message+"."
            logging.debug("Received request not valid: "+message+".")
            time.sleep (1)  
            socket.send("Invalid request!")

