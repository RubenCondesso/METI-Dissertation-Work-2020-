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


##################################################################################   Startup  ########################################################################################################################################################################################################################################################################################################################################################################################################################


# Lock to be used in accessing to data files
lock = threading.Semaphore()

# List with last 5 distances measured -> FIFO list
list_distances = deque([None] * 5)

# List with last 10 measured in the same second
timeInstance_measures = []

# List with potencial consecutive distances of a moving obstacle
movingObstacle_distances = []

##################################################################################   Functions  ########################################################################################################################################################################################################################################################################################################################################################################################################################


# ---------------------------------------------------------------------------- Obstacle Detection Thread -------------------------------------------------------------------------------------- #

# Obstacle Detection class
class Obstacle_Detection (threading.Thread):
    '''
        Thread that manages the obstacle detection process
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
            self.write_data()

        GPIO.cleanup()


    # Get the distance measurement to the obstacle detected
    def echo_signal(self):

        sleep(0.1)

        # Set TRIG as LOW
        GPIO.output(self.GPIO_TRIGGER, GPIO.LOW)

        #print "Waiting for the Sensor to settle"

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

        return distance


    # Calculate the most likely value for each obstacle detection
    def data_mean(self):

        global timeInstance_measures

        # Get new measures while list has not have 10 measurements
        while (len(timeInstance_measures) < 10):

            # Append new measure to the list
            timeInstance_measures.append(self.echo_signal())

        # eliminates values that fall beyond n (= 1) standard deviations from the mean of current list
        correct_list = [x for x in timeInstance_measures if abs(x - np.mean(timeInstance_measures)) < np.std(timeInstance_measures) * 1 ]

        # Reset list
        timeInstance_measures = []

        return np.mean(correct_list)


    # Generate CAM Messages
    def write_data(self):

        # Some gap between measurements
        sleep(1)

        # Get the distance measured for that time instance
        distance = self.data_mean()

        # Round to two decimal points
        distance = round(distance, 2)

        # Check whether the distance is within the sensor's range + some compensation
        if distance > 2 and distance < 450:

            # Distance measured by the Ultrasonic Sensor
            distance = distance + self.GPIO_OFFSET

            # Lock
            lock.acquire()

            try:

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
            #print("No obstacle detected")

            distance = 0

        return str(distance)


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


    '''
    # Get weighted average of last 6 distances measured
    def weighted_average(self, distance):

        # Save distance in distances list
        list_distances.pop()
        list_distances.appendleft(distance)

        # Check if the sensor already measured 8 distances so far
        if None not in list_distances:

            # Get weigthed average from last 6 distances measured - current distance + last 5 distances measured
            return np.average([distance, list_distances[0], list_distances[1], list_distances[2], list_distances[3], list_distances[4]], weights = [0.5, 0.15, 0.15, 0.10, 0.05, 0.05])

        return 0
    '''



# ---------------------------------------------------------------------------- Handler State Thread -------------------------------------------------------------------------------------- #

# HandlerState class
class HandlerState(threading.Thread):
    '''
        Thread responsible for setting the obstacle state - Idle or Active
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

        newlines = []

        global movingObstacle_distances

        try:

            with open("/home/pi/SmartBike/Output/detected_obstacles.txt", 'r') as f:

                # Sleep to acquire first some detections
                sleep(1)

                # Read all lines in the file so far
                all_lines = f.readlines()

                # Create list with size 3
                value_line = [None] * 3

                # when the file have at least 3 measurements
                if (len(all_lines) > 2):

                    # Get lines in groups of 3 lines consecutives
                    for i in range(0, len(all_lines), 3):

                        # Lock
                        lock.acquire()

                        value_line[i:i+3] = all_lines[i:i+3]

                        # Iterate over the 3 consecutive distances
                        for line in value_line:

                            line = line.split()

                            # The state of the obstacle has not been defined yet
                            if line[14] == "Unknown":

                                # Add distance to list
                                movingObstacle_distances.append(line[11])


                        # check if all 3 distance were added to list
                        if (len(movingObstacle_distances) == 3):

                            # difference between  the 3 consecutive distances
                            difference_distance = []

                            try:

                                # iterate over the list
                                for s in range(1, len(movingObstacle_distances)):

                                    difference_distance.append(abs(float(movingObstacle_distances[s]) - float(movingObstacle_distances[s-1])))


                                if (len(difference_distance) == 2):

                                    line_temp = [None] * 3
                                    line_temp[0] = value_line[i].split()
                                    line_temp[1] = value_line[i+1].split()
                                    line_temp[2] = value_line[i+2].split()

                                    # difference between 3 consecutive is always > 10 centimeters -> obstacle is moving
                                    if (difference_distance[0] > 10 and difference_distance[1] > 10):

                                        # Change the status
                                        value_line[i] =  value_line[i].replace(line_temp[0][14], "Moving")
                                        value_line[i+1] =  value_line[i+1].replace(line_temp[1][14], "Moving")
                                        value_line[i+2] =  value_line[i+2].replace(line_temp[2][14], "Moving")

                                    else:

                                        # Change the status
                                        value_line[i] =  value_line[i].replace(line_temp[0][14], "Immobile")
                                        value_line[i+1] =  value_line[i+1].replace(line_temp[1][14], "Immobile")
                                        value_line[i+2] =  value_line[i+2].replace(line_temp[2][14], "Immobile")


                                    # Write new lines to the file
                                    newlines.append(value_line[i])
                                    newlines.append(value_line[i+1])
                                    newlines.append(value_line[i+2])

                                    line_temp = [None] * 3


                            # No obstacle detected in this line of file
                            # Handle IOERROR exception
                            except OSError as e:
                                print "I/O error({0}: {1}".format(e.errno, e.strerror)

                            # Handle other exceptions such as atribute error
                            except:
                                print "Unexpected error: ", sys.exc_info()[0]


                            # Reset list
                            difference_distance = []

                            # Reset list
                            movingObstacle_distances = []

                        # Reset list
                        movingObstacle_distances = []

                        # Unlock
                        lock.release()

        # No obstacle detected in this line of file
        # Handle IOERROR exception
        except OSError as e:
            print "I/O error({0}: {1}".format(e.errno, e.strerror)

        # Handle other exceptions such as atribute error
        except:
            print "Unexpected error: ", sys.exc_info()[0]



        try:

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

        # No obstacle detected in this line of file
        # Handle IOERROR exception
        except OSError as e:
            print "I/O error({0}: {1}".format(e.errno, e.strerror)

        # Handle other exceptions such as atribute error
        except:
            print "Unexpected error: ", sys.exc_info()[0]



# -------------------------------------------------------------------------------------- Main function -------------------------------------------------------------------------------------- #

# Main function - Menu
def main():

    if os.path.exists("/home/pi/SmartBike/Output/detected_obstacles.txt") == False:

         # Lock
        lock.acquire()

        # Create the file for measures
        file_create = open("/home/pi/SmartBike/Output/detected_obstacles.txt","w+")
        file_create.close()

        # Unlock
        lock.release()

    else:

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
