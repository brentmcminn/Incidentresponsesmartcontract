from web3 import Web3 
import json
import os
import time
import subprocess

infura_url = "wss://kovan.infura.io/ws/v3/73150865c6e943d59cf17560170dbb85"

web3 = Web3(Web3.WebsocketProvider(infura_url))

with open("Lassie.json") as f:
    info_json = json.load(f)

abi = info_json

mycontract = web3.eth.contract(address='0xE917f5348ce9B6483ffdFb0D4F15bC029bed96c1', abi=abi)

def my_callback(event):
    print (f'{event} fired from contract')
    print(type(event))
    
def toDict(dictToParse):
    # convert any 'AttributeDict' type found to 'dict'
    parsedDict = dict(dictToParse)
    for key, val in parsedDict.items():
        # check for nested dict structures to iterate through
        if  'dict' in str(type(val)).lower():
            parsedDict[key] = toDict(val)
        # convert 'HexBytes' type to 'str'
        elif 'HexBytes' in str(type(val)):
            parsedDict[key] = val.hex()
    return parsedDict

myfilter = mycontract.events.publishWSContractState.createFilter(fromBlock=16207300)

while True:
   for event in myfilter.get_new_entries():
        event_dict = toDict(event)
        print(event_dict)
        if event_dict['args']['responderState']>2:
            #this launches the drone - there are two options, outdoor with gps or indoor demo. LEASH DRONE INDOORS!
            #subprocess.call(f"python gps_deploy_asset.py --latitude 30.1288942 --longitude -95.5063823",shell=True)
            subprocess.call(f"python indoor_deploy_asset.py",shell=True)


   time.sleep(2)





