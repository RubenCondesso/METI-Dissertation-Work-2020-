#!/usr/bin/python
#
# uart_peripheral.py - Class for the Raspberry Pi Zero
#
# 30 March 2020 - 2.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Python code that launch the BLE GATT Server and runs the UART Service -> to be connected to a Central Device (Smartphone)
#
#


# =================================================================================== Code starts here ===================================================================================== #

# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #

import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from gatt_advertisement import Advertisement
from gatt_advertisement import register_ad_cb, register_ad_error_cb
from gatt_server import Service, Characteristic
from gatt_server import register_app_cb, register_app_error_cb

# Import deque
from collections import deque

# Import calendar
import calendar

# Import Threads
import threading

# -------------------------------------------------------------------------------------- Startup ------------------------------------------------------------------------------------------- #

BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
LOCAL_NAME =                   'RPi-Sensing_System'

mainloop = None

# Flag that indicates if the service is ready or not
ready_flag = False

# Number of GPS coordenates received
count = 0

domain = [[None]*2 for _ in range(8)]

# Array with the last 8 GPS coordenates received
array_GPS = deque(domain)

# Dictionary that converts month name to integer
abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}


# Lock to be used in accessing to data files
lock = threading.Semaphore()

# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #


# Tx Characteristic Class
class TxCharacteristic(Characteristic):
    '''
        Enable notification for the TX Characteristic to receive data from the application
        The application transmits all data that is received over the UART as notifications
    '''

    # Init the Tx Characteristic
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = False

        # Send the data to Smartphone periodically
        GLib.timeout_add_seconds(2, self.read_Data)


    # Read the data obtained by the Sensing System
    def read_Data(self):
        '''
            Each message has {ID, Timestamp, obstacle's distance, obstacle's state, User's GPS coodenates}
        '''

        global ready_flag

        if ready_flag == True:

            # Lock
            lock.acquire()

            try:
                # Open the file with the sensor's data information
                data_file = open("/home/pi/SmartBike/Output/status_obstacles.txt", "r")

                # Read each line of the text file
                line = data_file.readlines()

                # Reset the file's data -> after being processed and send to Smartphone
                open("/home/pi/SmartBike/Output/status_obstacles.txt", "w").close()

                for x in line:

                    # Send the sensor's data to the smartphone
                    self.send_Data(x)

            # Handle IOERROR exception
            except OSError as e:
                print "I/O error({0}: {1}".format(e.errno, e.strerror)

            # Handle other exceptions such as atribute error
            except:
                print "Unexpected error: ", sys.exc_info()[0]

            # Unlock
            lock.release()

        return True


    # Send the Sensing System's data to the Smartphone
    def send_Data(self, s):

        if not self.notifying:
            return

        value = []

        try:
            for c in s:
                # Add the value received to the dbus
                value.append(dbus.Byte(c.encode()))

            # Change properties
            self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])

        # Handle IOERROR exception
        except OSError as e:
            print "I/O error({0}: {1}".format(e.errno, e.strerror)

        # Handle other exceptions such as atribute error
        except:
            print "Unexpected error: ", sys.exc_info()[0]


    # Start Notify
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True

    # Stop Notify
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False


# Rx Characteristic Class
class RxCharacteristic(Characteristic):
    '''
        Write data to the RX Characteristic to send it on to the UART interface
    '''

    # Init the Rx Characteristic
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)

    # Display the messages received from the Smartphone
    def WriteValue(self, value, options):

        # Received message
        msg_received = format(bytearray(value).decode())

        # Analyze the message received
        self.analyze_Message(msg_received)

        # Print the received message
        print('App - {}'.format(bytearray(value).decode()) + '\n')


    # Analyse each message received from the Smartphone
    def analyze_Message(self, msg):
        '''
            Check if a GPS coordenates was received; Start the obstacle detection when ready
        '''

        global ready_flag
        global count
        global array_GPS

        message = msg.split()

        # The connection was made -> is ready to start detect obstacles
        if count > 7:
            ready_flag = True

        # The connection was made -> wait for certain number of GPS coordenates first
        elif count <= 7:
            ready_flag = False
            count += 1

        # Received GPS coordenates
        if len(message) == 10 and message[0] == 'Updated' and message[1] == 'Location:':

            # Timestamp received
            time = str(message[6]) + " " + str(abbr_to_num[message[5]]) + " " + str(message[9]) + " " + str(message[7])

            # Array FIFO
            array_GPS.popleft()
            array_GPS.append((str(message[2]), time))


# UART Service initialize with two characteristics
class UartService(Service):

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(bus, 0, self))
        self.add_characteristic(RxCharacteristic(bus, 1, self))


# Initialize the Service Application
class Application(dbus.service.Object):

    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response


# Initialize UART Application
class UartApplication(Application):

    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(UartService(bus, 0))


# Initialize UART Service Advertisement
class UartAdvertisement(Advertisement):

    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True


# Find the adapter to be used
def find_adapter(bus):

    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
            return o
        print('Skip adapter:', o)

    return None


# -------------------------------------------------------------------------------------- Main function -------------------------------------------------------------------------------------- #

def main():

    global mainloop
    global adv

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)

    if not adapter:
        print('BLE adapter not found')
        return

    service_manager = dbus.Interface(
                                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    app = UartApplication(bus)
    adv = UartAdvertisement(bus, 0)

    mainloop = GLib.MainLoop()

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)
    ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)
    try:
        mainloop.run()
    except KeyboardInterrupt:

        # Release advertisement
        adv.Release()

# Main of this python code
#if __name__ == '__main__':
    #main()
