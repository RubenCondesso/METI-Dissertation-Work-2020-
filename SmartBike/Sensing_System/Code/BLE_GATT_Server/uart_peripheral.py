#!/usr/bin/python
#
# uart_peripheral.py - Class for the Raspberry Pi Zero
#
# 24 March 2020 - 2.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Python code that launch the BLE GATT Server and runs the UART Service -> to be connected to the UART Peripheral (Smartphone)
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

# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #

# Tx Characteristic Class
class TxCharacteristic(Characteristic):

    # Init the Tx Characteristic
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = False
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)

    # Read the input on console
    def on_console_input(self, fd, condition):
        s = fd.readline()
        if s.isspace():
            pass
        else:
            self.send_tx(s)
        return True

    # Send the data received
    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])

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

    # Init the Rx Characteristic
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)

        # Flag that indicates if the service is ready or not
        self.ready_flag = False

        # Number of GPS coordenates received
        self.count = 0

    # Print the messages received from the Smartphone
    def WriteValue(self, value, options):

        # Received message
        msg_received = format(bytearray(value).decode())

        # Analyze the message received
        self.analyze_Message(msg_received)
        print('App - {}'.format(bytearray(value).decode()) + '\n')

    def analyze_Message(self, msg):

        message = msg.split()

        # The connection was made -> is ready to start detect obstacles
        if self.count > 4:
            self.ready_flag = True

        # The connection was made -> wait for certain number of GPS coordenates first
        elif self.count <= 4:
            self.ready_flag = False
            self.count += 1

        # Received GPS coordenates
        elif len(message) == 3 and message[0] == 'Updated' and message[1] == 'Location:':

            coordenates = message[2]

            GPS_coord = (coordenates.split())

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
