#!/usr/bin/python
#
# cpu_module.py - Class for the Raspberry Pi Zero
#
# 24 March 2020 - 2.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# TO COMPLETE
#


# =================================================================================== Code starts here ===================================================================================== #


# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #

import sys, os

import uart_peripheral, uart_Communication, gatt_advertisement, gatt_server, obstacles_Distances

# Import Threads
import threading

# Import time and sleep library
from time import sleep, time

# Import datetime class
from datetime import datetime

# Import GPIO library
import RPi.GPIO as GPIO


# -------------------------------------------------------------------------------------- Startup ------------------------------------------------------------------------------------------- #

# Flag that indicates if the detection of obstacles was already started
flag = 0

# ----------------------------------------------------------------------------------- Main function ---------------------------------------------------------------------------------------- #

# Creates a thread that launchs the uart peripheral service
class thread_thread_uartpheral(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.kill_received = False

    def run(self):
        while self.kill_received == False:
            self.start_thread_uartperipheral()

    def start_thread_uartperipheral(self):
        try:
            uart_peripheral.main()
        except:
            raise


# Creates a thread that launchs the obstacle detection
class thread_ObstaclesDistance(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.kill_received = False


    def run(self):
        while self.kill_received == False:
            self.start_ObstacleDistance()

        print("\n---- Terminating Sensing System program ----")
        print("Cleaning up GPIO pins...")

        # Clean the GPIO pins
        GPIO.cleanup()

        print("Done.")


    def start_ObstacleDistance(self):

        try:
            obstacles_Distances.main()
        except:
            raise


# -------------------------------------------------------------------------------------- Main function -------------------------------------------------------------------------------------- #


# Main of this python code
def main():

    global flag

    thread_uart = thread_thread_uartpheral()
    thread_uart.start()

    while thread_uart.isAlive():

        try:
            #Synchronization timeout of threads kill
            thread_uart.join(1)

            # Service is ready to start detecting obstacles
            if uart_peripheral.ready_flag == True and flag == 0:

                flag = 1

                thread_obsDist = thread_ObstaclesDistance()
                thread_obsDist.start()

            elif flag == 1:
                thread_obsDist.join(1)

        except KeyboardInterrupt:
            # Ctrl-C handling and send kill to threads
            thread_uart.kill_received = True

            (uart_peripheral.adv).Release()

            if flag == 1:
                thread_obsDist.kill_received = True

            # Exit the function
            try:
                sys.exit(0)

            except SystemExit:
                os._exit(0)


# Main of this python code
if __name__ == "__main__":
   main()
