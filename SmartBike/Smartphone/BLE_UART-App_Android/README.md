# BLE_UART-App_Android
==================================================================================================================================================================================================================

SmartBike System's App used to send/receive data to the Sensing System (Raspberry Pi Zero), using Bluetooth Low Energy. The Sensing System runs a BLE GATT server, and its used a Bluetooth Low Energy UART service to send and receive the data between both components. This app handles 128 bit proprietary UUID service and characteristics (Rx and Tx).

Make sure Bluetooth is enabled on the smartphone, and give it to the app permissions to access the location of the Smartphone (in its settings). Once started the app will immediately search for BLE devices and connect to the first one it finds with the UART service (Raspberry Pi Zero). Status messages will be displayed in a text view on the screen.

Once you see the connected and services discovered message, data can be exchange between the Smartphone and the Sensing System.


This source code can be compiled with Android Studio and Gradle.

### Note:

- Android 4.3 or later is required.

- Android Studio supported.

==================================================================================================================================================================================================================

## Ruben Condesso - Master Thesis in Telecommunications and Computer Engineering


