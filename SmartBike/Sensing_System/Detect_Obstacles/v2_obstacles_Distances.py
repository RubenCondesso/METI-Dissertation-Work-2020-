#!/usr/bin/python
#
# obstacles_Distances.py - Ultrasonic Sensor Class for the Raspberry Pi Zero
#
# 01 March 2020 - 2.0 
# 
# Autor: Ruben Condesso - 81969 - 2nd Semester (2020)
#
# 
# SmartBike System - Master Thesis in Telecomunications and Computer Engineering
#
# 
# Python code that measures the distance to obstacles detected by the ultrasonic sensor
# 
#

# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #

# Import GPIO library
import RPi.GPIO as GPIO

# Import time and sleep library
from time import sleep, time

# Import datetime class
from datetime import datetime

import os, signal

# Import socket library
import socket

# Import fcntl library
import fcntl

# Import struct library
import struct

# ----------------------------------------------------------------------------------- Code starts here -------------------------------------------------------------------------------------- #

# Ultrasonic sensor class 
class Ultrasonic_Sensor():
  
    
    def __init__(self, GPIO_TRIGGER, GPIO_ECHO, GPIO_OFFSET = 0.5):

        # Set GPIO pin numbering - GPIO Mode (BOARD/BCM)
        GPIO.setmode(GPIO.BCM)
     
        # Sensor instance for Trigger
        self.GPIO_TRIGGER = GPIO_TRIGGER

        # Sensor instance for Echo
        self.GPIO_ECHO = GPIO_ECHO

        # Sensor instance for calibration factor
        self.GPIO_OFFSET = GPIO_OFFSET            

        # GPIO setup
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)                  
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)   



    def __str__(self):

        # Return a string that representates the sensor attributes
        return "Ultrasonic Sensor: TRIGGER - {0}, ECHO - {1}, OFFSET: {2} cm".format(self.GPIO_TRIGGER, self.GPIO_ECHO, self.GPIO_OFFSET)


    # Get the current timestamp of each obstacle detection
    def timestamp(self):

        # Datetime object containing the local date and time
        dateTimeObj = datetime.now()

        # Timestamp with date and hour
        total_timestamp = [0, 0]

        # Date of the obstacle detection
        current_date = []

        current_date.append(dateTimeObj.day)
        current_date.append(dateTimeObj.month)
        current_date.append(dateTimeObj.year)
        
        # Hour of the obstacle detection
        current_hour = []
        current_hour.append(dateTimeObj.hour)
        current_hour.append(dateTimeObj.minute)
        current_hour.append(dateTimeObj.second)
        current_hour.append(dateTimeObj.microsecond)

        total_timestamp[0] = current_date
        total_timestamp[1] = current_hour 

        return total_timestamp


    # Get the IP of the Raspberry Pi Zero
    def getIP_RPizero(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Name of the network interface
        ifname = "wlan0"

        # IP of the Raspberry Pi Zero
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])



    # Get the distance measurement to the obstacle detected
    def echo_signal(self):

        # Set TRIG as LOW
        GPIO.output(self.GPIO_TRIGGER, GPIO.LOW)     

        print "Waiting for the Sensor to settle."
        
        # Some gap between measurements
        sleep(1)      

        # Set the Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, GPIO.HIGH)

        # Delay 10 us
        sleep(0.00001)

        # Set TRIG as LOW
        GPIO.output(self.GPIO_TRIGGER, GPIO.LOW)

        # Check whether the ECHO is LOW
        while GPIO.input(self.GPIO_ECHO) == GPIO.LOW:    

            # Saves the last known time of LOW pulse
            pulse_start = time()      


        # Check whether the ECHO is HIGH 
        while GPIO.input(self.GPIO_ECHO) == GPIO.HIGH:        
            
            # Saves the last known time of HIGH pulse
            pulse_end = time()                       


        # Time difference between start and arrival - Get pulse duration to a variable
        pulse_duration = pulse_end - pulse_start 

        # Distance = 17160.5 * Time (unit cm) at sea level and at 20 degrees
        distance = pulse_duration * 17160.5  

        # Round to two decimal points            
        distance = round(distance, 2)

        # Check whether the distance is within the sensor's range
        if distance > 2 and distance < 400: 

            distance = distance + self.GPIO_OFFSET
            
            print("Obstacle detected")

        else:

            distance = 0
            print("No obstacle detected.") 

        return str(distance)     


# Main function - Menu
def main():

    # New sensor on GPIO pins: Trigger - 18 & Echo - 24
    sensor = Ultrasonic_Sensor(18, 24)       

    # Open the text file
    data_file = open("ultrasonicSensor_Data.txt","w+")

    def endProcess(signum = None, frame = None):

        # Called on process termination. 
        if signum is not None:

            SIGNAL_NAMES_DICT = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n )
            print("signal {} received by process with PID {}".format(SIGNAL_NAMES_DICT[signum], os.getpid()))

        print("\n-- Terminating program --")
        print("Cleaning up GPIO...")

        # Clean the GPIO pins
        GPIO.cleanup()

        print("Done.")
        exit(0)

    # Assign handler for process exit
    signal.signal(signal.SIGTERM, endProcess)
    signal.signal(signal.SIGINT, endProcess)
    signal.signal(signal.SIGHUP, endProcess)
    signal.signal(signal.SIGQUIT, endProcess)

    while True:
        
        # Get the ID of Raspberry Pi Zero
        rpi_ID = sensor.getIP_RPizero()

        # Get the timestamp of this exact moment
        present_timestamp = sensor.timestamp()

        # Get the distance obtained in this exact moment
        present_distance = sensor.echo_signal()

        # Add this distance to the text file
        data_file.write("ID: " + rpi_ID + " | " + "Timestamp: " + str(present_timestamp) + " | " + "Obstacle distance: " + present_distance + "\n")

    # Close the text file
    data_file.close()



# Main of this python code
if __name__ == "__main__":

    # execute only if run as a script
    main()
