#!/usr/bin/python
# RS_UltraSonic.py - Ultrasonic Sensor Class for the Raspberry Pi 
#
# 15 March 2017 - 1.0 Original Issue
#
# Reefwing Software
# Simplified BSD Licence - see bottom of file.

import RPi.GPIO as GPIO
import os, signal

from time import sleep, time

# Private Attributes
__CALIBRATE      = "1"
__TEST           = "2"
__FILTER         = "3"
__QUIT           = "q"

class UltraSonic():
    # Ultrasonic sensor class 
    
    def __init__(self, TRIG, ECHO, offset = 0.5):
        # Create a new sensor instance
        self.TRIG = TRIG
        self.ECHO = ECHO
        self.offset = offset            # Sensor calibration factor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)                  
        GPIO.setup(self.ECHO, GPIO.IN)                   

    def __str__(self):
        # Return string representation of sensor
        return "Ultrasonic Sensor: TRIG - {0}, ECHO - {1}, Offset: {2} cm".format(self.TRIG, self.ECHO, self.offset)

    def ping(self):
        # Get distance measurement
        GPIO.output(self.TRIG, GPIO.LOW)            # Set TRIG LOW
        sleep(0.1)                                  # Min gap between measurements        
        # Create 10 us pulse on TRIG
        GPIO.output(self.TRIG, GPIO.HIGH)           # Set TRIG HIGH
        sleep(0.00001)                              # Delay 10 us
        GPIO.output(self.TRIG, GPIO.LOW)            # Set TRIG LOW
        # Measure return echo pulse duration
        while GPIO.input(self.ECHO) == GPIO.LOW:    
            pulse_start = time()                         

        while GPIO.input(self.ECHO) == GPIO.HIGH:        
            pulse_end = time()                           

        pulse_duration = pulse_end - pulse_start 
        # Distance = 17160.5 * Time (unit cm) at sea level and 20C
        distance = pulse_duration * 17160.5              
        distance = round(distance, 2)                    

        if distance > 2 and distance < 400:              
            distance = distance + self.offset
            print("Distance: ", distance," cm")
        else:
            distance = 0
            print("No obstacle")                         
        return distance

    def calibrate(self):
        # Calibrate sensor distance measurement
        while True:
            self.ping()
            response = input("Enter Offset (q = quit): ")
            if response == __QUIT:
                break;
            sensor.offset = float(response)
            print(sensor)
            
    @staticmethod
    def low_pass_filter(value, previous_value, beta):
        # Simple infinite-impulse-response (IIR) 
        # single-pole low-pass filter.
        # ß = discrete-time smoothing parameter 
        # (determines smoothness). 0 < ß < 1
        # LPF: Y(n) = (1-ß)*Y(n-1) + (ß*X(n))) 
        #           = Y(n-1) - (ß*(Y(n-1)-X(n)))
        smooth_value = previous_value - (beta * (previous_value -    value))
        return smooth_value
        

def main():
    sensor = UltraSonic(8, 7)       # new sensor on GPIO pins 7 & 8
    print(sensor)

    def endProcess(signum = None, frame = None):
        # Called on process termination. 
        if signum is not None:
            SIGNAL_NAMES_DICT = dict((getattr(signal, n), n) for n in dir(signal) if n.startswith('SIG') and '_' not in n )
            print("signal {} received by process with PID {}".format(SIGNAL_NAMES_DICT[signum], os.getpid()))
        print("\n-- Terminating program --")
        print("Cleaning up GPIO...")
        GPIO.cleanup()
        print("Done.")
        exit(0)

    # Assign handler for process exit
    signal.signal(signal.SIGTERM, endProcess)
    signal.signal(signal.SIGINT, endProcess)
    signal.signal(signal.SIGHUP, endProcess)
    signal.signal(signal.SIGQUIT, endProcess)

    while True:
        action = input("\nSelect Action - (1) Calibrate, (2) Test, or (3) Filter: ")

        if action == __CALIBRATE:
            sensor.calibrate()
        elif action == __FILTER:
            beta = input("Enter Beta 0 < ß < 1 (q = quit): ")
            filtered_value = 0
            if beta == __QUIT:
                break;
            while True:
                filtered_value = sensor.low_pass_filter(sensor.ping(), filtered_value, float(beta))
                filtered_value = round(filtered_value, 2)
                print("Filtered: ", filtered_value, " cm")
        else:
            sensor.ping()

if __name__ == "__main__":
    # execute only if run as a script
    main()

## Copyright (c) 2017, Reefwing Software
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
## 1. Redistributions of source code must retain the above copyright notice, this
##   list of conditions and the following disclaimer.
## 2. Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.