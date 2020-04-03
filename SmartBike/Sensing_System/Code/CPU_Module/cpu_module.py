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

import sys

import uart_peripheral, uart_Communication, gatt_advertisement, gatt_server, obstacles_Distances

# Import Threads
import threading

# Import time and sleep library
from time import sleep, time

# Import datetime class
from datetime import datetime


# -------------------------------------------------------------------------------------- Startup ------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------- Main function ---------------------------------------------------------------------------------------- #

# Creates a thread that launchs the uart peripheral service
class thread_UartPeripheral(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.kill_received = False

    def run(self):
        while self.kill_received == False:
            self.start_UartPeripheral()

    def start_UartPeripheral(self):
          uart_peripheral.main()


# Creates a thread that launchs the obstacle detection
class thread_ObstaclesDistance(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.kill_received = False


    def run(self):
        while self.kill_received == False:
            self.start_ObstacleDistance()

    def start_ObstacleDistance(self):
        print("Comecei a thread dos obstacles")

        #while uart_peripheral.RxCharacteristic.Ready_Flag == True:
            #obstacles_Distances.main()



# -------------------------------------------------------------------------------------- Main function -------------------------------------------------------------------------------------- #


# Main of this python code
def main():

    uartPeri = thread_UartPeripheral()
    uartPeri.start()

    while uartPeri.isAlive():
        try:
            #Synchronization timeout of threads kill
            uartPeri.join(1)

        except KeyboardInterrupt:
            uartPeri.kill_received = True

    #obsDist = thread_ObstaclesDistance()
    #obsDist.start()


# Main of this python code
if __name__ == "__main__":

   main()
