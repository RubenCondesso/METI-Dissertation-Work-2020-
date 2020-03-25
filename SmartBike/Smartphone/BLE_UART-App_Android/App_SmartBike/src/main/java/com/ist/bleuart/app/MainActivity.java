/*
#
# MainActivity.java - Java Class of Android App
#
# 23 March 2020 - 1.0 
# 
# Autor: Ruben Condesso - 81969 - 2nd Semester (2020)
#
# 
# SmartBike System - Master Thesis in Telecomunications and Computer Engineering
#
# 
# Java class that sends and receives data to a Bluetooth Low Energy UART service, which is running on the Raspberry Pi Zero (BLE GATT Server)
#
# */ 


/*
# =================================================================================== Code starts here =====================================================================================#
*/ 


/*
# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #
*/ 

package com.ist.bleuart.app;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothAdapter.LeScanCallback;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.os.Bundle;
import android.view.Menu;

import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import android.content.ComponentName;
import android.os.IBinder;

import static android.Manifest.permission.ACCESS_FINE_LOCATION;

/*
# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #
*/

public class MainActivity extends AppCompatActivity {

    // UUIDs for UAT service and associated characteristics
    public static UUID UART_UUID = UUID.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E");
    public static UUID TX_UUID = UUID.fromString("6E400002-B5A3-F393-E0A9-E50E24DCCA9E");
    public static UUID RX_UUID = UUID.fromString("6E400003-B5A3-F393-E0A9-E50E24DCCA9E");

    // UUID for the BLE client characteristic -> necessary for notifications
    public static UUID CLIENT_UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");

    // UI elements
    private TextView messages;
    private EditText input;

    // BLE state
    private BluetoothAdapter adapter;
    private BluetoothGatt gatt;
    private BluetoothGattCharacteristic tx;
    private BluetoothGattCharacteristic rx;

    private final int PERMISSION_REQUEST_CODE = 200;

    public BackgroundLocationService gpsService;
    public boolean mTracking = false;

    // BLE device callbacks -> Handles the main logic of this class
    private BluetoothGattCallback callback = new BluetoothGattCallback() {

        // Function called whenever the device connection state changes -> from disconnected state to connected state
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {

            super.onConnectionStateChange(gatt, status, newState);

            // Different states that can exist or change to

            if (newState == BluetoothGatt.STATE_CONNECTED) {
                writeLine("Connected to GATT Server - Sensing System :)");

                if (!gatt.discoverServices()) {
                    writeLine("Failed to start discovering services :(");
                }
            }
            else if (newState == BluetoothGatt.STATE_DISCONNECTED) {
                writeLine("Disconnected from GATT Server.");
            }
            else {
                writeLine("Connection state changed.  New state: " + newState);
            }
        }

        // Function called when service have been discovered on the remote device (Raspberry Pi Zero)
        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {

            super.onServicesDiscovered(gatt, status);

            if (status == BluetoothGatt.GATT_SUCCESS) {
                writeLine("Sensing System Service discovery completed.");
            }
            else {
                writeLine("Sensing System Service discovery failed with status: " + status);
            }

            // Save reference to each characteristic -> Read and Write
            tx = gatt.getService(UART_UUID).getCharacteristic(TX_UUID);
            rx = gatt.getService(UART_UUID).getCharacteristic(RX_UUID);

            // Setup notifications on RX characteristic changes -> Data received

            // (first) Call setCharacteristicNotification to enable notification
            if (!gatt.setCharacteristicNotification(rx, true)) {
                writeLine("Could not set notifications for RX characteristic.");
            }

            // (next) Update the RX characteristic's client descriptor to enable notifications
            if (rx.getDescriptor(CLIENT_UUID) != null) {
                BluetoothGattDescriptor desc = rx.getDescriptor(CLIENT_UUID);
                desc.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
                if (!gatt.writeDescriptor(desc)) {
                    writeLine("Could not write RX client descriptor value.");
                }
            }
            else {
                writeLine("Could not get RX client descriptor.");
            }
        }

        // Called when a remote characteristic changes -> like the RX characteristic
        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {

            super.onCharacteristicChanged(gatt, characteristic);
            writeLine("Received from the Sensing System: " + characteristic.getStringValue(0));
        }
    };

    // BLE device scanning callback
    private LeScanCallback scanCallback = new LeScanCallback() {

        // Funcction called when the GATT Server (RPi Zero) is found
        @Override
        public void onLeScan(BluetoothDevice bluetoothDevice, int i, byte[] bytes) {

            writeLine("Found device: " + bluetoothDevice.getAddress());

            // Check if the device has the UART service
            if (parseUUIDs(bytes).contains(UART_UUID)) {

                // Found the device -> stop the scanning
                adapter.stopLeScan(scanCallback);

                writeLine("Found the UART service.");

                // Connect to the GATT Server - Raspberry Pi Zero
                // Control flow will now go to the callback functions when BLE events occur
                gatt = bluetoothDevice.connectGatt(getApplicationContext(), false, callback, 2);
            }
        }
    };

    // OnCreate -> called once to initialize the activity
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Grab the references to the UI elements
        messages = (TextView) findViewById(R.id.messages);
        input = (EditText) findViewById(R.id.input);

        adapter = BluetoothAdapter.getDefaultAdapter();

        /*
        // Prepare the location service
        final Intent intent = new Intent(this.getApplication(), BackgroundLocationService.class);
        this.getApplication().startService(intent);
        this.getApplication().bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE);

        // Start the track of the user's location
        startTracking();

         */

    }

    // OnResume -> called right before UI is displayed.
    // Start the BLE connection
    @Override
    protected void onResume() {

        super.onResume();

        // Scan for all BLE devices
        // The first one with the UART service (RPi Zero) will be chosen 
        writeLine("Scanning for devices...");
        adapter.startLeScan(scanCallback);
    }

    // OnStop _> called right before the activity loses foreground focus
    // Close the BLE connection
    @Override
    protected void onStop() {

        super.onStop();
        if (gatt != null) {

            gatt.disconnect();
            gatt.close();
            gatt = null;
            tx = null;
            rx = null;
        }
    }

    // Handler for click on the send button
    public void sendClick(View view) {

        String message = input.getText().toString();
        if (tx == null || message == null || message.isEmpty()) {
            // Do nothing if there is no device or message to send
            return;
        }

        // Update TX characteristic value
        // Note the setValue overload that takes a byte array must be used
        tx.setValue(message.getBytes(Charset.forName("UTF-8")));
        if (gatt.writeCharacteristic(tx)) {
            writeLine("Sent from App: " + message);
        }
        else {
            writeLine("Could not write TX characteristic.");
        }
    }

    // Write data to the messages text view
    // Care is taken to do this on the main UI thread so writeLine can be called from any thread (like the BLE callback)
    private void writeLine(final CharSequence text) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                messages.append(text);
                messages.append("\n");
            }
        });
    }

    // Workaround function from the SO thread to manually parse advertisement data
    private List<UUID> parseUUIDs(final byte[] advertisedData) {
        List<UUID> uuids = new ArrayList<UUID>();

        int offset = 0;
        while (offset < (advertisedData.length - 2)) {
            int len = advertisedData[offset++];
            if (len == 0)
                break;

            int type = advertisedData[offset++];
            switch (type) {
                case 0x02: // Partial list of 16-bit UUIDs
                case 0x03: // Complete list of 16-bit UUIDs
                    while (len > 1) {
                        int uuid16 = advertisedData[offset++];
                        uuid16 += (advertisedData[offset++] << 8);
                        len -= 2;
                        uuids.add(UUID.fromString(String.format("%08x-0000-1000-8000-00805f9b34fb", uuid16)));
                    }
                    break;
                case 0x06:// Partial list of 128-bit UUIDs
                case 0x07:// Complete list of 128-bit UUIDs

                    // Loop through the advertised 128-bit UUID's
                    while (len >= 16) {
                        try {
                            // Wrap the advertised bits and order them.
                            ByteBuffer buffer = ByteBuffer.wrap(advertisedData, offset++, 16).order(ByteOrder.LITTLE_ENDIAN);
                            long mostSignificantBit = buffer.getLong();
                            long leastSignificantBit = buffer.getLong();
                            uuids.add(new UUID(leastSignificantBit,
                                    mostSignificantBit));
                        } catch (IndexOutOfBoundsException e) {
                            continue;
                        } finally {
                            // Move the offset to read the next uuid
                            offset += 15;
                            len -= 16;
                        }
                    }
                    break;
                default:
                    offset += (len - 1);
                    break;
            }
        }
        return uuids;
    }

    // Boilerplate code from the activity creation
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {

        // Inflate the menu -> This adds items to the action bar if it is present
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    /*
    public void startTracking() {

        //check for permission
        if (ContextCompat.checkSelfPermission(getApplicationContext(), ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            gpsService.startTracking();
            mTracking = true;
        } else {
            ActivityCompat.requestPermissions(this, new String[]{ACCESS_FINE_LOCATION}, PERMISSION_REQUEST_CODE);
        }
    }

    private ServiceConnection serviceConnection = new ServiceConnection() {
        public void onServiceConnected(ComponentName className, IBinder service) {
            String name = className.getClassName();
            if (name.endsWith("BackgroundLocationService")) {
                gpsService = ((BackgroundLocationService.LocationServiceBinder) service).getService();
            }
        }

        public void onServiceDisconnected(ComponentName className) {
            if (className.getClassName().equals("BackgroundLocationService")) {
                gpsService = null;
            }
        }
    };
    */
}