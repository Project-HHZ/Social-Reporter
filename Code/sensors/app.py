import paho.mqtt.client as mqtt
import time
import zmq
import logging
import datetime


#Declare&init vars
port = "45157"
now = datetime.datetime.now()
scriptPath = "/home/pi/IoT/sensors/"

#Init logging
logging.basicConfig(filename=scriptPath+'sensors.log',level=logging.DEBUG)
logging.debug("##################"+str(now)+"###################")
logging.debug("MQTT started")


#Init Server connection
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

MQTT_SERVER = "127.0.0.1"
MQTT_PATH = "#"
MQTT_USER = 'user'
MQTT_PASS = 'pass'

sensorName = "hhz/125/1/1/1/0/16"

# The callback for when the client receives a CONNACK response from the serv$
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    logging.debug("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logging.debug(msg.topic+" "+str(msg.payload))
    
    if msg.topic == sensorName:
        print("Bewegung erkannt...")
        logging.debug("Bewegung erkannt...")
        socket.send_string ("SRCaptureImage#sensors")
        message = socket.recv()
        print ("Received reply: "+str(message))
        logging.debug("Received reply: "+str(message))
        time.sleep(10)
        #Init connection

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username="digitalhhz",password="hackathon")
client.connect(MQTT_SERVER, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
