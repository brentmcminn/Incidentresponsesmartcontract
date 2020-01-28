# This folder contains 6 files
## 1) arduino_to_pi.ino - Reads analog sensors (temp and smoke) and sends data over serial port to Raspberry Pi. 
## 2) pizero_aws_iot.py - Sends data from the Raspberry pi sensors to AWS IOT 
## 3) set_smoke_temp.py - Streams AWS Appsync live data and calls smart contract function via Web3.py to set smoke and temperature threshold breached boolean value.
## 3) monitor_contract.py - Listens to events on smart contract using Web3.py.  Opens a subprocess to launch a script to deploy drone (see below).
## 5) and 6) indoor_deploy_asset.py and gps_deploy_asset.py are used to send commands to drone.  Only one file used at a time.    

# Must have drone on a leash to use indoor_deploy_asset.py !!!