import numpy as np
import cv2
import time
import zmq
import logging
import datetime

#Declare&init vars
now = datetime.datetime.now()
port = "45157"
filePath = "/home/pi/IoT/faceDetection/"

#Init logging
logging.basicConfig(filename=filePath+'faceDetection.log',level=logging.DEBUG)

#Init zmq socket 
context = zmq.Context()
socket = context.socket(zmq.REQ)

# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades
#faceCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
faceCascade = cv2.CascadeClassifier(filePath+'haarcascade/haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(1)
cap.set(3,1280) # set Width
cap.set(4,720) # set Height

oldepoch = time.time()
i = True

print("FaceDetection started")
logging.debug("#################"+str(now)+"####################")
logging.debug("FaceDetection started")

while True:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(20, 20)
    )

    if i == True:
	logging.debug("FaceDetection running...")
	i = False

    if time.time() - oldepoch >= 10 and len(faces) >= 1:
          print("Two or more faces detected")
          logging.debug("Two or more faces detected")

          #Connect to captureServer 
          socket.connect ("tcp://localhost:%s" % port)
          socket.send ("SRCaptureImage#faceDetection")
          #Get the reply.
          message = socket.recv()
          print "Received reply ", message

          #Reset timer
	  oldepoch = time.time()

    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

    #cv2.imshow('video',img)

    k = cv2.waitKey(30) & 0xff
    if k == 27: # press 'ESC' to quit
        break

cap.release()
cv2.destroyAllWindows()
