from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time
import zmq
import logging

#Declare&init vars
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
PORT = "45157"
NOW = datetime.datetime.now()
SCRIPT_PATH = "/home/pi/IoT/calendar/"


def main():

    #Init logging
    logging.basicConfig(filename=SCRIPT_PATH+'calendar.log',level=logging.DEBUG)
    logging.debug("##################"+str(NOW)+"###################")
    logging.debug("Google Calendar API started...")

    #Init connection
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect ("tcp://localhost:%s" % PORT)



    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
               SCRIPT_PATH+'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(SCRIPT_PATH+'token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    while True:
       logging.debug("Druchlauf")
       # Call the Calendar API
       now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
       events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=1, singleEvents=True,
                                        orderBy='startTime').execute()

       events = events_result.get('items', [])
       
       #Debug Google API Result
       #for x in events:
       #    print (x)

       try:
           for event in events:
               start = event['start'].get('dateTime', event['start'].get('date'))
               end = event['end'].get('dateTime', event['end'].get('date'))
               location =  event['location']
               if (start <= now  <= end) and ("HHZ" in location) and ("125" in location):
                  print(str(NOW)+": Between", start, "--", now, "--", end+" Betreff: "+event['summary'])
                  logging.debug(event['summary'])
                  logging.debug(str(NOW)+": Between"+str(start)+"--"+str(now)+"--"+str(end)+" Betreff: "+event['summary'])
                  socket.send_string ("SRStartRecording#calendar#"+event['summary'])
                  #Get the reply.
                  message = socket.recv()
                  print ("Received reply: "+str(message))
                  logging.debug("Received reply "+str(message))
               else:
                  print(str(NOW)+": No meeting at the moment!")
                  logging.debug(str(NOW)+": No meeting at the moment!")
                  socket.send_string ("SRStopRecording#calendar")
                  #Get the reply.
                  message = socket.recv()
                  print ("Received reply: "+str(message))
                  logging.debug("Received reply "+str(message))
       except Exception as ex:
               print ("Exception: "+str(ex))
               print(str(NOW)+": No meeting at the moment! Exception thrown")
               logging.debug(str(NOW)+": No meeting at the moment!")
               socket.send_string ("SRStopRecording#calendar")
               #Get the reply.
               message = socket.recv()
               print ("Received reply: "+str(message))
               logging.debug("Received reply "+str(message))

       time.sleep(60)

if __name__ == '__main__':
    main()
