#!/usr/bin/python
#
# ultrasonic_sensor.py - Ultrasonic Sensor Class for the Raspberry Pi Zero
#
# 17 April 2020 - 3.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Python code that measures the distance to obstacles detected by the ultrasonic sensor
#
#


# =================================================================================== Code starts here =====================================================================================#



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

# Import Threads
import threading

# Import os.path
import os.path

# Import sys
import sys

# Import Math
import math

# Import Numpy
import numpy as np

# Import deque
from collections import deque

# Import uart_peripheral code
import uart_peripheral


# --------------------------------------------------------------------------------------- Startup ------------------------------------------------------------------------------------------- #

# Lock to be used in accessing to data files
lock = threading.Semaphore()

# List with last 5 distances measured -> FIFO list
list_distances = deque([None] * 5)

# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #

# Ultrasonic sensor class
class Obstacle_Detection (threading.Thread):
    '''
        Thread that writes the detected obstacle distances to the text file
    '''

    # Init
    def __init__(self, GPIO_TRIGGER, GPIO_ECHO, GPIO_OFFSET = 0.5):

        threading.Thread.__init__(self)
        self.kill_received = False

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


    # Run thread
    def run (self):

        while self.kill_received == False:
            self.echo_signal()

        GPIO.cleanup()


    # Get the distance measurement to the obstacle detected
    def echo_signal(self):

        # Set TRIG as LOW
        GPIO.output(self.GPIO_TRIGGER, GPIO.LOW)

        #print "Waiting for the Sensor to settle"

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

        # Check whether the distance is within the sensor's range + some compensation
        if distance > 2 and distance < 450:

            # Distance measured by the Ultrasonic Sensor
            distance = distance + self.GPIO_OFFSET

            #print("Distance before: ")
            #print(distance)

            # Check if the weighted average was calculated
            if self.weighted_average(distance) != 0:

                # Lock
                lock.acquire()

                try:

                    # Transform measured distance in the weighted of that distance
                    distance = self.weighted_average(distance)

                    #print("Distance after: ")
                    #print(distance)

                    # Open the text file
                    data_file = open("/home/pi/SmartBike/Output/detected_obstacles.txt","a")

                    # Get the ID of Raspberry Pi Zero
                    rpi_ID = self.getIP_RPizero()

                    # Get the timestamp of this exact moment
                    present_timestamp = self.current_timestamp()

                    # GPS coordenates of the Smartphone when the obstacle was detected
                    gps_coordenates = self.setGPS_Coordenates(uart_peripheral.array_GPS, present_timestamp)

                    # Add this distance to the text file
                    data_file.write("ID: " + rpi_ID + " | " + "Timestamp: " + str(present_timestamp) + " | " + "Obstacle distance: " + str(distance) + " | " + "State: Unknown" + " | " "GPS Coordinates: " + str(gps_coordenates[0]) + "\n")

                    #print("Obstacle detected")

                    # Close the text file
                    data_file.close()

                # Handle IOERROR exception
                except OSError as e:
                    print "I/O error({0}: {1}".format(e.errno, e.strerror)

                # Handle other exceptions such as atribute error
                except:
                    print "Unexpected error: ", sys.exc_info()[0]

                # Unlock
                lock.release()

            else:
                print("Weight average distance could not be calculated")

        else:

            #print("No obstacle detected")

            distance = 0

        return str(distance)

    # Get weighted average of last 6 distances measured
    def weighted_average(self, distance):
        '''
            Distances Weights:
                . current distance - 0.3
                . last distance measured - 0.15
                . penultimate distance measured - 0.15
                . antepenultimate distance measured - 0.1
                . remaining two distances measured - 0.05 + 0.05
        '''

        # Save distance in distances list
        list_distances.pop()
        list_distances.appendleft(distance)

        # Check if the sensor already measured 8 distances so far
        if None not in list_distances:

            # Get weigthed average from last 6 distances measured - current distance + last 5 distances measured
            return np.average([distance, list_distances[0], list_distances[1], list_distances[2], list_distances[3], list_distances[4]], weights = [0.5, 0.15, 0.15, 0.10, 0.05, 0.05])

        return 0


    # Get the IP of the Raspberry Pi Zero
    def getIP_RPizero(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Name of the network interface
        ifname = "wlan0"

        # IP of the Raspberry Pi Zero
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])


    # Get the current timestamp of each obstacle detection
    def current_timestamp(self):

        # Datetime object containing the local date and time
        dateTimeObj = datetime.now()

        if len(str(dateTimeObj.day)) == 1:
            dayTime = "0" + str(dateTimeObj.day)

        else:
            dayTime = str(dateTimeObj.day)

        # Timestamp with date and hour
        total_timestamp = []

        total_timestamp = str(dayTime) + " " + str(dateTimeObj.month) + " " + str(dateTimeObj.year) + " " + str(dateTimeObj.hour) + ":" + str(dateTimeObj.minute) + ":" + str(dateTimeObj.second)

        return total_timestamp


    # Set the GPS coordenates received from the smartphone for the timestamp in handle when the obstacle was detected
    def setGPS_Coordenates(self, gpsDeque, timestamp_App):
        '''
            Check the time difference between the current timestamp with the timestamp of the GPS coordenates received
            If the difference is small -> Save the GPS coordenates to current obstacle detected (write to file)
            If the difference is too big -> Read the GPS coordenates save in the list, make prediction of the user's position (taking into account his speed)
        '''

        # Count of iterations
        count = 0

        for i in gpsDeque:

            # GPS coordenate of the current timestamp -> last one of the deque
            if count == (len(gpsDeque)-1):

                time_deque = i[1].split()
                time_current = timestamp_App.split()

                time_difference = self.calculate_diffTime(time_deque, time_current)

                # Time difference is acceptable
                if time_difference <= 15:

                    # GPS coordenates
                    return i

                # Time difference is too big -> too much time withou receiving GPS coordenates
                else:
                    '''
                        Make GPS coordenates prediction taking into account the positions registered in the GPS list
                    '''

                    # Distance travelled in the last coordinates received (from list) - in km
                    distance_total = self.calculate_distance(gpsDeque)

                    # Time between first timestamp and last timestamp (from list) - in hours
                    time_total = self.calculate_time(gpsDeque)

                    # Prediction of the user's speed -> Speed = distance/time
                    speed = int(distance_total) / (float(time_total))

                    # Get prediction of the user's location
                    return self.predict_location(gpsDeque, speed, time_total)

            count += 1



    # Difference between two datetime objects in seconds
    def calculate_diffTime(self, time1, time2):

        # Time saved on deque -> Datetime object
        time_deque_object = datetime.strptime(time1[len(time1)-1], '%H:%M:%S')

        # Current time -> Date time object
        time_current_object = datetime.strptime(time2[len(time2)-1], '%H:%M:%S')

        return (abs(time_current_object - time_deque_object)).total_seconds()


    # Haversine distance function
    def calculate_distance(self, list_GPS):
        '''
            Calculate geographic distance between list of coodinates(latitude, longitude)
        '''

        results = []

        for i in range(1, len(list_GPS)):

            list_loc1 = []
            for z in ((list_GPS[i-1])[0]).split(','):
                z = float(z)
                list_loc1.append(z)

            lat1 = list_loc1[0]
            lng1 = list_loc1[1]

            list_loc2 = []
            for x in ((list_GPS[i])[0]).split(','):
                x = float(x)
                list_loc2.append(x)

            lat2 = list_loc2[0]
            lng2 = list_loc2[1]

            degreesToRadians = (math.pi / 180)
            latrad1 = lat1 * degreesToRadians
            latrad2 = lat2 * degreesToRadians
            dlat = (lat2 - lat1) * degreesToRadians
            dlng = (lng2 - lng1) * degreesToRadians

            a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(latrad1) * math.cos(latrad2) * math.sin(dlng / 2) * math.sin(dlng / 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            r = 6371000 # Earth radius

            results.append(r * c)

        # Result in km
        return (sum(results) / 1000)


    # Calculate the time that the user took from the first GPS coordenates until the last ones present on the list
    def calculate_time(self, list_GPS):

        # First timestamp on the list
        time_first = (list_GPS[0])[1]

        # Last timestamp on the list
        time_last = (list_GPS[-1])[1]

        # Month number has only 1 number
        if len(time_first) == 18 and len(time_last) == 18:

            time_first = time_first[10:]
            time_last = time_last[10:]
            start_object = datetime.strptime(time_first, '%H:%M:%S')
            end_object = datetime.strptime(time_last, '%H:%M:%S')

            # Result in hours
            return ((abs(end_object - start_object)).total_seconds())/3600

         # Month number has only 2 number
        elif len(time_first) == 19 and len(time_last) == 19:

            time_first = time_first[11:]
            time_last = time_last[11:]
            start_object = datetime.strptime(time_first, '%H:%M:%S')
            end_object = datetime.strptime(time_last, '%H:%M:%S')

            # Result in hours
            return ((abs(end_object - start_object)).total_seconds())/3600

        # Something went wrong
        else:
            return None


    # Predict the user's location - GPS coordinates
    def predict_location(self, list_GPS, user_speed, user_time):

        radiusEarthKm = 6371 # Earth radius in km

        # Distance travelled
        kmdistance = user_speed * user_time
        distRatio = kmdistance / radiusEarthKm

        distRatioSine = math.sin(distRatio)
        distRatioCosine = math.cos(distRatio)

        for i in range(1, len(list_GPS)):
            list_loc1 = []
            for z in ((list_GPS[i-1])[0]).split(','):
                z = float(z)
                list_loc1.append(z)
            lat1 = list_loc1[0]
            lng1 = list_loc1[1]

            list_loc2 = []
            for x in ((list_GPS[i])[0]).split(','):
                x = float(x)
                list_loc2.append(x)
            lat2 = list_loc2[0]
            lng2 = list_loc2[1]

        degreesToRadians = (math.pi / 180)

        latrad1 = lat1 * degreesToRadians
        latrad2 = lat2 * degreesToRadians
        lngrad2 = lng2 * degreesToRadians

        dlat = (lat2 - lat1) * degreesToRadians
        dlng = (lng2 - lng1) * degreesToRadians

        angle = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(latrad1) * math.cos(latrad2) * math.sin(dlng / 2) * math.sin(dlng / 2)
        anglerad = angle * degreesToRadians

        startLatCos = math.cos(latrad2)
        startLatSin = math.sin(latrad2)
        startLonRad = math.sin(lngrad2)

        endLatRads = math.asin((startLatSin * distRatioCosine) + (startLatCos * distRatioSine * math.cos(angle)))
        endLonRads = startLonRad + math.atan2(math.sin(angle) * distRatioSine * startLatCos, distRatioCosine - startLatSin * math.sin(endLatRads))

        # Expected Latitude
        newLat = endLatRads / degreesToRadians

        # Excepted Longitude
        newLong = endLonRads / degreesToRadians

        newCoord = str(newLat) + "," + str(newLong)

        newTimestamp = self.current_timestamp()

        return (newCoord, newTimestamp)



# HandlerState class
class HandlerState(threading.Thread):
    '''
        Thread responsible for read the text files and change the obstacle state - Idle or Active
    '''

    # Init
    def __init__(self):

        threading.Thread.__init__(self)
        self.kill_received = False


    # Run thread
    def run (self):

        while self.kill_received == False:
            self.check_obstacleState()


    # Check the state of the obstacle
    def check_obstacleState(self):

        value_previous = 0

        newlines = []

        with open("/home/pi/SmartBike/Output/detected_obstacles.txt", 'r') as f:

            # Do a small sleep to acquire first some detection
            sleep(1.1)

            for line in f.readlines():

                # Lock
                lock.acquire()

                value_line = line.split()

                # The state of the obstacle has not been defined yet
                if value_line[14] == "Unknown":

                    try:
                        # If difference between two consecutives measurements is small -> obstacles is  motionless
                        if abs(float(value_line[11]) - value_previous) < 20:

                            # Change the status
                            line = line.replace(value_line[14], "Immobile")

                        else:

                            # Change the status
                            line = line.replace(value_line[14], "Moving")

                        value_previous = float(value_line[11])

                        newlines.append(line)

                    # No obstacle detected in this line of file
                    # Handle IOERROR exception
                    except OSError as e:
                        print "I/O error({0}: {1}".format(e.errno, e.strerror)

                    # Handle other exceptions such as atribute error
                    except:
                        print "Unexpected error: ", sys.exc_info()[0]

                # Unlock
                lock.release()

        # Lock
        lock.acquire()

        try:
            # Reset the file's data
            open("/home/pi/SmartBike/Output/detected_obstacles.txt", "w").close()

        # Handle IOERROR exception
        except OSError as e:
            print "I/O error({0}: {1}".format(e.errno, e.strerror)

        # Handle other exceptions such as atribute error
        except:
            print "Unexpected error: ", sys.exc_info()[0]

        # Unlock
        lock.release()

        # Set the status of detection made
        with open("/home/pi/SmartBike/Output/status_obstacles.txt", 'w') as f:

            for line in newlines:

                # Lock
                lock.acquire()

                try:
                    # Write to the file the detection made with right/real status
                    f.write(line)

                # No write to be made
                # Handle IOERROR exception
                except OSError as e:
                    print "I/O error({0}: {1}".format(e.errno, e.strerror)

                # Handle other exceptions such as atribute error
                except:
                    print "Unexpected error: ", sys.exc_info()[0]

                # Unlock
                lock.release()



# -------------------------------------------------------------------------------------- Main function -------------------------------------------------------------------------------------- #


# Main function - Menu
def main():

    if os.path.exists("/home/pi/SmartBike/Output/detected_obstacles.txt") == False:

        # Create the file for measures
        file_create = open("/home/pi/SmartBike/Output/detected_obstacles.txt","w+")
        file_create.close()

    # Run the ultrasonic sensor wtih this GPIO pins: Trigger - 18 & Echo - 24
    sensor = Obstacle_Detection(18, 24)
    sensor.start()

    # Run the Handler Thread
    state = HandlerState()
    state.start()

    print("\n---- Starting the Sensing System ----\n")

    while sensor.isAlive():

        try:
            # Synchronization timeout of threads kill
            sensor.join(1)
            state.join(1)

        except KeyboardInterrupt:

            sensor.kill_received = True
            state.kill_received = True

            print("\n---- Terminating Sensing System program ----")

            print("Cleaning up GPIO pins...")

            # Clean the GPIO pins
            GPIO.cleanup()

            print("Done.")

            try:
                sys.exit(0)

            except SystemExit:
                os._exit(0)


# Main of this python code
#if __name__ == "__main__":

    # execute only if run as a script
    #main()
