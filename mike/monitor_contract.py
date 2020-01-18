from web3 import Web3 
import json
import os
import time

infura_url = "wss://kovan.infura.io/ws/v3/73150865c6e943d59cf17560170dbb85"

web3 = Web3(Web3.WebsocketProvider(infura_url))

with open("contract_abi.json") as f:
    info_json = json.load(f)

abi = info_json

mycontract = web3.eth.contract(address='0x091FDeb7990D3E00d13c31b81841d56b33164AD7', abi=abi)

def my_callback(event):
    print (f'{event} fired from contract')

myfilter = mycontract.events.currentResponderState.createFilter(fromBlock=16147303)

while True:
   for event in myfilter.get_new_entries():
        my_callback(event)
   time.sleep(2)





