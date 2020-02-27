
# Python code that measures the distance to obstacles detected by the ultrasonic sensor


# Libraries
import RPi.GPIO as GPIO
import time

# ----------------------------------------- Code starts here --------------------------------------------------------- #


# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
# Set the GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
# Set the GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Measure the distance to the detected obstacle 
def obstacle_distance():

    # Set the Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # Set the Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    startTime = time.time()
    stopTime = time.time()
 
    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        startTime = time.time()
 
    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        stopTime = time.time()
 
    # Time difference between start and arrival
    timeElapsed = stopTime - startTime
    
    # Multiply with the sound speed (34300 cm/s) and divide by two, because it's an echo signal (back and forth)
    # Conversion of value obtained to a distance in cm
    total_distance = (timeElapsed * 34300) / 2

    #Distance to the detected obstacle
    distance = total_distance / 2

    return distance

# Main function
if __name__ == '__main__':

    try:
        while True:
            dist = obstacle_distance()
            print ("Obstacle detected at %.1f cm." % dist)
            time.sleep(1)
 
        # Reset the code by pressing CTRL + C
    except KeyboardInterrupt:
        print("Obstacle detection stopped by User.")
        GPIO.cleanup()