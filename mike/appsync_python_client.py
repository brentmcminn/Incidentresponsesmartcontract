import requests
import subprocess
import json
import paho.mqtt.client as mqtt
from urllib.parse import urlparse

# the AppSync graphql endpoint for your API
apiurl = 'https://vvkmaenj5bctdfr5cwu35lrh44.appsync-api.us-east-1.amazonaws.com/graphql'

# replace X-Api-Key with a valid API key
postHeaders = {
    'Content-Type': 'application/json',
    'X-Api-Key': 'da2-iymnyu7ryzh47bkg4uza25xhfm'
}

# a valid subscription type from your schema
payload = {"query": "subscription \n OnUpdateSensor{onUpdateSensor(id: \"PiZero\")\n {id,temp,smoke,lat,long,timestamp}}"}



# make the subscription request to the server and extract the presigned URL and topic information
r = requests.post(apiurl, headers=postHeaders, json=payload) 
print(r)

# grab the necessary items out of the "extentions" object returned by the POST request
client_id = r.json()['extensions']['subscription']['mqttConnections'][0]['client']
ws_url = r.json()['extensions']['subscription']['mqttConnections'][0]['url']
topic = r.json()['extensions']['subscription']['mqttConnections'][0]['topics'][0]

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload_str = msg.payload.decode('utf-8')
    payload_json = json.loads(payload_str)
    #print(msg.topic + " " + str(msg.payload))
    smoke = payload_json['data']['onUpdateSensor']['smoke']
    temp = payload_json['data']['onUpdateSensor']['temp']
    latitude = round(payload_json['data']['onUpdateSensor']['lat'],7)
    longitude = round(payload_json['data']['onUpdateSensor']['long'],7)
    print(f'temp: {temp}, smoke: {smoke}, lat: {latitude}, long: {longitude}')
    if payload_json['data']['onUpdateSensor']['smoke'] > 200:
        subprocess.call(f"python gps_deploy_asset.py --latitude {latitude} --longitude {longitude}",shell=True)
        client.disconnect()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)

# parse the websockets presigned url
urlparts = urlparse(ws_url)

headers = {
    "Host": "{0:s}".format(urlparts.netloc),
}

client = mqtt.Client(client_id=client_id, transport="websockets")
client.on_connect = on_connect
client.on_message = on_message

client.ws_set_options(path="{}?{}".format(urlparts.path, urlparts.query), headers=headers)
client.tls_set()

print("trying to connect now....")
client.connect(urlparts.netloc, 443)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()