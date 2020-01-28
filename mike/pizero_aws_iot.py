

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import serial
import logging
import time
import json
import argparse
import pynmea2



# Function called when a shadow is updated
def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("temperature: " + str(payloadDict["state"]["reported"]["temperature"]))
        print("smoke: " + str(payloadDict["state"]["reported"]["smoke"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

# Function called when a shadow is deleted
def customShadowCallback_Delete(payload, responseStatus, token):

     # Display status and data from delete request
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


# Read in command-line parameters
def parseArgs():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

    args = parser.parse_args()
    return args


# Configure logging
# AWSIoTMQTTShadowClient writes data to the log
def configureLogging():

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


# Parse command line arguments
args = parseArgs()

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)

# If no --port argument is passed, default to 8883
if not args.port: 
    args.port = 8883


# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(args.clientId)
myAWSIoTMQTTShadowClient.configureEndpoint(args.host, args.port)
myAWSIoTMQTTShadowClient.configureCredentials(args.rootCAPath, args.privateKeyPath, args.certificatePath)

# AWSIoTMQTTShadowClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10) # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(10) # 5 sec


# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a device shadow handler, use this to update and delete shadow document
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(args.thingName, True)

# Delete curent shadow JSON doc
deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

###CREATE PAYLOAD BELOW

#initializing temp and smoke variables so program will not error out before it syncs with serial data n 
bluetooth_serial = serial.Serial("/dev/rfcomm0", baudrate = 9600, timeout = 0.5)
serialport = serial.Serial("/dev/ttyACM0", 9600, timeout = 0.5)
serialport.flush()
reading_string = ""
temp=""
smoke=""
payload = {}
last_payload = {}
coordinates = {}
#hardcoding geo coordinates of sensor to location of Rim Fire in 2013


#read serial stream
while True:
    #json object built for smoke and temp
    reading = serialport.read()
    reading_decoded = reading.decode('utf-8')
    reading_string = reading_string + reading_decoded
    
    if "," in reading_string:
        temp = reading_string.strip(" ,")
        temp = int(temp)
        reading_string = ""
    elif ";" in reading_string:
        smoke = reading_string.strip(" ;")
        smoke = int(smoke)
        reading_string = ""
    else:
        pass
    
    #json object built for gps over bluetooth, to hardcode gps comment out below and set coordinates variable above
    gps_stream = bluetooth_serial.readline()
    gps_stream_decoded = gps_stream.decode('ascii')
    
    if "$GPRMC" in gps_stream_decoded:
        gps_data = pynmea2.parse(gps_stream_decoded)
        lat = gps_data.latitude
        long = gps_data.longitude
        coordinates = {"lat":lat,"long":long}
    
    payload = {"state":{"reported":{"temperature":temp,"smoke":smoke,"coordinates":coordinates}}}    # Create message payload
    

    # Update shadow with payload - check if any values have changed before sending to AWS IoT
    if last_payload != payload:
        deviceShadowHandler.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 5)
        last_payload = payload
        serialport.flush()
    
    