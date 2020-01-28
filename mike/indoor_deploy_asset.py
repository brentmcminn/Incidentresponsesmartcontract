##ONLY USE WITH A DRONE ON A LEASH  -- DRONE WILL FLY OFF

from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math
#from appsync_python_client import smoke

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Control Copter and send commands in GUIDED mode ')
parser.add_argument('--connect',default='udp:0.0.0.0:14550',
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
#print('Connecting to vehicle on: %s' % connection_string)

vehicle = connect(connection_string, wait_ready=True)

def arm_and_takeoff_nogps(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude without GPS data.
    """

    ##### CONSTANTS #####
    

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    # If you need to disable the arming check,
    # just comment it with your own responsibility.
    #while not vehicle.is_armable:
     #   print(" Waiting for vehicle to initialise...")
      #  time.sleep(1)


    print("Arming motors")
    # Copter should arm in GUIDED_NOGPS mode
    #vehicle.mode = VehicleMode("GUIDED_NOGPS")
    vehicle.mode = VehicleMode("ALT_HOLD")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        vehicle.armed = True
        time.sleep(1)

    print("Taking off!")
    
        
    print("Taking off to desired altitude: %s" % aTargetAltitude)
    if (vehicle.location.global_relative_frame.alt <= aTargetAltitude):
        print("Vehicle Altitude: %s" % vehicle.location.global_relative_frame.alt)
        vehicle.channels.overrides[3] = 1800
        time.sleep(10)
        
    
    



# Take off 2.5m in GUIDED_NOGPS mode.
arm_and_takeoff_nogps(20)

# Hold the position for 3 seconds.



#print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")
time.sleep(1)

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()

print("Completed")