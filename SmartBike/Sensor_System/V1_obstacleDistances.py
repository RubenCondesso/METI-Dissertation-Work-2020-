#!/usr/bin/python
#
# obstacleDistances.py - Ultrasonic Sensor Class for the Raspberry Pi Zero
#
# 28 Fev 2020 - 1.0 
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

# Import time library
import time



# ----------------------------------------------------------------------------------- Code starts here -------------------------------------------------------------------------------------- #


# Set GPIO pin numbering - GPIO Mode (BOARD/BCM)
GPIO.setmode(GPIO.BCM)
 
# Associate pin 18 to TRIG
GPIO_TRIGGER = 18

# Associate pin 24 to ECHO
GPIO_ECHO = 24
 

print "Distance measurement in progress"


# Set the GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Measure the distance to the detected obstacle 
def obstacle_distance():

    # Set TRIG as LOW
    GPIO.output(GPIO_TRIGGER, False)

    print "Waiting for the Sensor to settle."

    # Delay of 2 seconds
    time.sleep(2)      

    # Set the Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)      

    # Delay of 0.00001 seconds
    time.sleep(0.00001)                      
    
    # Set TRIG as LOW
    GPIO.output(GPIO_TRIGGER, False)                             
 
    pulse_start = time.time()
    pulse_end = time.time()
 
    # Check whether the ECHO is LOW
    while GPIO.input(GPIO_ECHO) == 0:
        
        # Saves the last known time of LOW pulse
        pulse_start = time.time()

 
    # Check whether the ECHO is HIGH
    while GPIO.input(GPIO_ECHO) == 1:

        # Saves the last known time of HIGH pulse 
        pulse_end = time.time()


    # Time difference between start and arrival - Get pulse duration to a variable
    pulse_duration = pulse_end - pulse_start
    
    # Multiply pulse duration by 17150 to get distance
    distance = pulse_duration * 17150        
    
    # Round to two decimal points
    distance = round(distance, 2)           

    # Check whether the distance is within range
    if distance > 2 and distance < 400:      

        return distance
    
    else:                 
        
        return False




# Main function
if __name__ == '__main__':

    try:
        while True:

            dist = obstacle_distance()

            #print ("Obstacle detected at %.1f cm." % dist)

            if dist != False:

                # Print the distance to the obstacle with a 0.5 cm calibration
                print "Obstacle detected at ",dist - 0.5,"cm."  

                time.sleep(1)

            else:

                # Display out of range
                print "Out Of Range" 

                time.sleep(1)


 
    # Reset the code by pressing CTRL + C
    except KeyboardInterrupt:

        print("Obstacle detection stopped by User.")
        
        GPIO.cleanup()