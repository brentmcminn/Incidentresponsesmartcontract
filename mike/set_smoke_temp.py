#This script 
import requests
import os
import subprocess
import json
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
from web3 import Web3 


##Setting up eth account, contract and connection through Infura
#Infure
infura_url = "wss://kovan.infura.io/ws/v3/73150865c6e943d59cf17560170dbb85"

web3 = Web3(Web3.WebsocketProvider(infura_url))

#Account
key_lassie = os.getenv('key_lassie')

with open("keystore.json") as f:
    keystore_json = json.load(f)

keystore = keystore_json

private_key = web3.eth.account.decrypt(keystore,key_lassie)

acct = web3.eth.account.privateKeyToAccount(private_key)

ether_address = acct.address

# Contract
with open("Lassie.json") as x:
    info_json = json.load(x)

abi = info_json

mycontract = web3.eth.contract(address='0xE917f5348ce9B6483ffdFb0D4F15bC029bed96c1', abi=abi)






# the AppSync graphql endpoint for your API
apiurl = 'https://vvkmaenj5bctdfr5cwu35lrh44.appsync-api.us-east-1.amazonaws.com/graphql'

# replace X-Api-Key with a valid API key
postHeaders = {
    'Content-Type': 'application/json',
    'X-Api-Key': 'da2-hst3p4dorvanrpo3gbgwob2hfi'
}

# a valid subscription type from your schema
#payload = {"query": "subscription \n OnUpdateSensor{onUpdateSensor(id: \"Pi4\")\n {id,temp,smoke,lat,long,timestamp}}"}
payload = {"query": "subscription \n OnUpdateSensor{onUpdateSensor(id: \"PiZero\")\n {id,temp,smoke,lat,long,timestamp}}"}
#payload = {"query": "subscription \n OnUpdateSensor{onUpdateSensor\n {id,temp,smoke,lat,long,timestamp}}"}



# make the subscription request to the server and extract the presigned URL and topic information
r = requests.post(apiurl, headers=postHeaders, json=payload) 


print(r)



# grab the necessary items out of the "extentions" object returned by the POST request
client_id = r.json()['extensions']['subscription']['mqttConnections'][0]['client']
ws_url = r.json()['extensions']['subscription']['mqttConnections'][0]['url']
topic = r.json()['extensions']['subscription']['mqttConnections'][0]['topics'][0]



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global temp_high
    global smoke_high
    payload_str = msg.payload.decode('utf-8')
    payload_json = json.loads(payload_str)
    #print(msg.topic + " " + str(msg.payload))
    smoke = payload_json['data']['onUpdateSensor']['smoke']
    temp = payload_json['data']['onUpdateSensor']['temp']
    latitude = round(payload_json['data']['onUpdateSensor']['lat'],7)
    longitude = round(payload_json['data']['onUpdateSensor']['long'],7)
    
    print(f'temp: {temp}, smoke: {smoke}, lat: {latitude}, long: {longitude}')
    if payload_json['data']['onUpdateSensor']['smoke'] > 200:
        smoke_high = True
        smoke_action(latitude,longitude)
        
    if payload_json['data']['onUpdateSensor']['smoke'] < 200: 
        smoke_high = False       

    if payload_json['data']['onUpdateSensor']['temp'] > 32:
        temp_high = True
        temp_action(latitude,longitude)

    if payload_json['data']['onUpdateSensor']['temp'] < 32:
        temp_high = False       
    #subprocess.call(f"python gps_deploy_asset.py --latitude {latitude} --longitude {longitude}",shell=True)
        #subprocess.call(f"python deploy_assets.py" ,shell=True)
       
        

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

mqtt.Client.smoke_flag = False

client.ws_set_options(path="{}?{}".format(urlparts.path, urlparts.query), headers=headers)
client.tls_set()
client.on_connect = on_connect

print("trying to connect now....")
client.connect(urlparts.netloc, 443)





client.on_message = on_message

#take_action variables act as switches so function will only run once
smoke_take_action = True
temp_take_action = True

#Ethereum transactions setup

def smoke_action(sensor_lat,sensor_long):
    sensor_lat = sensor_lat
    sensor_long = sensor_long
    global smoke_high
    global smoke_take_action
    global private_key

    nonce_smoke = web3.eth.getTransactionCount(ether_address)

    transaction_smoke = mycontract.functions.setSmoke(
        True,
        'PiZero' ).buildTransaction({
        'gas': 100000,
        'gasPrice': web3.toWei('1', 'gwei'),
        'from': ether_address,
        'nonce': nonce_smoke
        }) 

    signed_txn_smoke = web3.eth.account.signTransaction(transaction_smoke, private_key=private_key)

    if smoke_high and smoke_take_action:
        print(f"smoke breached at coordinates{sensor_lat}, {sensor_long}")
        #subprocess.call(f"python gps_deploy_asset.py --latitude {sensor_lat} --longitude {sensor_long}",shell=True)
        web3.eth.sendRawTransaction(signed_txn_smoke.rawTransaction)
        smoke_take_action = False
        

def temp_action(sensor_lat,sensor_long):
    sensor_lat = sensor_lat
    sensor_long = sensor_long
    global temp_high
    global temp_take_action
    global private_key
    
    nonce_temp = web3.eth.getTransactionCount(ether_address)

    transaction_temp = mycontract.functions.setTemperature(
        True,
        'PiZero' ).buildTransaction({
        'gas': 100000,
        'gasPrice': web3.toWei('1', 'gwei'),
        'from': ether_address,
        'nonce': nonce_temp
        }) 

    signed_txn_temp = web3.eth.account.signTransaction(transaction_temp, private_key=private_key)

    if temp_high and temp_take_action:
        print(f"temp breached at coordinates{sensor_lat}, {sensor_long}")
        web3.eth.sendRawTransaction(signed_txn_temp.rawTransaction)
        temp_take_action = False
        



# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()