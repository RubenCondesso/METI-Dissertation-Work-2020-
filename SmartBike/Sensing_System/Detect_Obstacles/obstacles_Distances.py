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

import os, signal

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
            print("Obstacle detected at: ", distance," cm")

        else:

            distance = 0
            print("No obstacle detected.") 

        return str(distance)     


# Main function - Menu
def main():

    # New sensor on GPIO pins: Trigger - 18 & Echo - 24
    sensor = Ultrasonic_Sensor(18, 24)       

    print(sensor)

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
        
        # Get the distance obtained in this exact moment
        present_distance = sensor.echo_signal()
        
        # Add this distance to the text file
        data_file.write(present_distance + "\n")

    # Close the text file
    data_file.close()



# Main of this python code
if __name__ == "__main__":

    # execute only if run as a script
    main()
