from web3.auto.infura import w3
import json
import os

with open("contract_abi.json") as f:
    info_json = json.load(f)
abi = info_json
mycontract = w3.eth.contract(address='0x091FDeb7990D3E00d13c31b81841d56b33164AD7', abi=abi)
myfilter = mycontract.events.currentResponderState.createFilter(fromBlock=16147303)
#myfilter.fromBlock = "16181508"
#mycontract.eventFilter('currentResponderState', {'fromBlock': 16181508,'toBlock': 'latest'})
print(abi)
print (myfilter)