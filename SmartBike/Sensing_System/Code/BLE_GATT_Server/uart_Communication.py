#!/usr/bin/python
#
# uart_Communication.py - Class for the Raspberry Pi Zero
#
# 24 March 2020 - 2.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# BLE GATT UART Service that receives and writes data and serves as a bridge to the UART interface.
#
#
# In this case, this peripheral (Raspberry Pi Zero) will be connected to one central device (Smartphone)
#
# The peripheral (GATT Server) holds the ATT lookup data and service and characteristic definitions, and the GATT Client (smarthphone) sends requests to this server.
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


# -------------------------------------------------------------------------------------- Startup ------------------------------------------------------------------------------------------- #

BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'

# Write data to the RX Characteristic to send it on to the UART interface
UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'

# Enable notifications for the TX Characteristic to receive data from the application, where the application transmits all data that is received over UART as notifications
UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'

LOCAL_NAME =                   'RPi-Sensing_System'
mainloop = None


# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #

# Characteristic for read data
class TxCharacteristic(Characteristic):
    # To receive data coming from the TX Characteristic, enable notifications after the service discovery.

    # Init the uart peripheral
    def __init__(self, bus, index, service):

        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = False
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.read_SensorData)


    # Read the data obtained by the ultrasonic sensor
    def read_SensorData(self, fd, condition):

        s = fd.readline()

        if s.isspace():
            pass

        else:

            # Open the file with the sensor's data information
            data_file = open("/home/pi/SmartBike/Sensing_System/ultrasonicSensor_Data.txt")

            # Read each line of the text file
            line = data_file.readlines()

            for x in line:

                # Send the sensor's data to the smartphone
                self.send_SensorData(x)

        return True


    # Send the distances to the obstacle, detected by the ultrasonic sensor
    def send_SensorData(self, s):

        if not self.notifying:
            return

        value = []

        for c in s:

            # Add the value received to the dbus
            value.append(dbus.Byte(c.encode()))

        # Change properties
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])



    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False


# Characteristic for sending data
class RxCharacteristic(Characteristic):
    # The sending procedure is asynchronous, so the data to be sent must remain valid until a dedicated callback notifies you that the Write Request has been completed.

    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)

    def WriteValue(self, value, options):
        print('remote: {}'.format(bytearray(value).decode()))


# Service with two Characteristics: one for read data and other to send data
class UartService(Service):

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(bus, 0, self))
        self.add_characteristic(RxCharacteristic(bus, 1, self))


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


# Launch the application for the uart service
class UartApplication(Application):

    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(UartService(bus, 0))


# Bluetooth Low Energy UART Service Advertisement
class UartAdvertisement(Advertisement):

    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True


# Find the BLE adapter to connect
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

    # Set the new main loop as the default for all new Connection or Bus instances
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # Connect to the system bus
    bus = dbus.SystemBus()

    # Find the BLE adapter to get a connection
    adapter = find_adapter(bus)

    if not adapter:
        print(' The BLE adapter was not found.')
        return


    service_manager = dbus.Interface(
                                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)

    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)


    app = UartApplication(bus)
    adv = UartAdvertisement(bus, 0)

    # Main event loop
    mainloop = GLib.MainLoop()

    # Run the application for this connection
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    # Advertise the Raspberry Pi Zero BLE connection
    ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    try:
        mainloop.run()

    except KeyboardInterrupt:
        adv.Release()



# Main of this python code
if __name__ == '__main__':
    main()
