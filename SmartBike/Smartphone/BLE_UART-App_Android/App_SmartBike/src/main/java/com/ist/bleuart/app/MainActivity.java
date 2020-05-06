/*
#
# MainActivity.java - Java Class of Android App
#
# 26 March 2020 - 2.0
# 
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
# 
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
# 
# Java class that represents the main activity of the App
#
# Sends and receives data to a Bluetooth Low Energy UART service, which is running on the Raspberry Pi Zero (BLE GATT Server)
#
# Tracks the user's location in time -> GPS coordinates
#
# */ 


/*
# =================================================================================== Code starts here =====================================================================================#
*/ 


/*
# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #
*/

package com.ist.bleuart.app;


import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothAdapter.LeScanCallback;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.view.Menu;

import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Scanner;
import java.util.UUID;
import androidx.core.app.ActivityCompat;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.maps.model.LatLng;

import java.util.Calendar;

/*
# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #
*/

// Main activity of the App
public class MainActivity extends Activity implements GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener, com.google.android.gms.location.LocationListener {

    // UUIDs for UAT service and associated characteristics
    public static UUID UART_UUID = UUID.fromString("6E400001-B5A3-F393-E0A9-E50E24DCCA9E");
    public static UUID TX_UUID = UUID.fromString("6E400002-B5A3-F393-E0A9-E50E24DCCA9E");
    public static UUID RX_UUID = UUID.fromString("6E400003-B5A3-F393-E0A9-E50E24DCCA9E");

    // UUID for the BLE client characteristic -> necessary for notifications
    public static UUID CLIENT_UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");

    // UI elements
    private TextView messages;
    private EditText input;

    // BLE state/features
    private BluetoothAdapter adapter;
    private BluetoothGatt gatt;
    private BluetoothGattCharacteristic tx;
    private BluetoothGattCharacteristic rx;

    private static final String TAG = "MainActivity";

    // Textview to display on the screen
    //private TextView mLatitudeTextView;
    //private TextView mLongitudeTextView;

    // Data class represents a geographic location
    private Location mLocation;

    // Obtains periodic updates of the device's geographical location
    private LocationManager mLocationManager;
    private LocationManager locationManager;

    // Request a quality of service for location updates
    private LocationRequest mLocationRequest;

    // Provides a common entry point to Google Play services and manages the network connection between the user's device and each Google service
    private GoogleApiClient mGoogleApiClient;

    // Receives notifications from the api when the location has changed
    private com.google.android.gms.location.LocationListener listener;

    private long UPDATE_INTERVAL = 2 * 1000;  /* 10 secs */
    private long FASTEST_INTERVAL = 2000; /* 2 sec */

    private static final int MY_PERMISSIONS_REQUEST_READ_FINE_LOCATION = 100;

    // Initialize database
    DataBase_CAM mDatabase;

    // OnCreate -> called once to initialize the activity
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // check the user's permissions
        boolean permissionGranted = ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;

        if(permissionGranted) {
        } else {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, 200);
        }

        // Grab the references to the UI elements
        messages = (TextView) findViewById(R.id.messages);
        input = (EditText) findViewById(R.id.input);

        mDatabase = new DataBase_CAM(this);

        adapter = BluetoothAdapter.getDefaultAdapter();

        //mLatitudeTextView = (TextView) findViewById((R.id.latitude_textview));
        //mLongitudeTextView = (TextView) findViewById((R.id.longitude_textview));

        mGoogleApiClient = new GoogleApiClient.Builder(this)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .build();

        mLocationManager = (LocationManager)this.getSystemService(Context.LOCATION_SERVICE);

        checkLocation(); //check whether location service is enable or not in your  phone

    }

    // OnResume -> called right before UI is displayed
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

        if (mGoogleApiClient.isConnected()) {
            mGoogleApiClient.disconnect();
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        switch (requestCode) {
            case 200: {
                if(grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    // {Some Code}
                }
            }
        }
    }


/*
# ------------------------------------------------------------------------------------ GPS Functions -------------------------------------------------------------------------------------------- #
*/

    // When the device is connected on the app
    @Override
    public void onConnected(Bundle bundle) {

        // Check for the permissions on Access Fine Location and Access Coarse Location
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            return;
        }

        // Start updating the location of the device
        startLocationUpdates();

        // Get current location
        mLocation = LocationServices.FusedLocationApi.getLastLocation(mGoogleApiClient);

        if(mLocation == null){

            startLocationUpdates();
        }
        if (mLocation != null) {

            // mLatitudeTextView.setText(String.valueOf(mLocation.getLatitude()));
            // mLongitudeTextView.setText(String.valueOf(mLocation.getLongitude()));

        } else {

            // Display pop up on screen with the values
            //Toast.makeText(this, "Location not Detected", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public void onConnectionSuspended(int i) {
        Log.i(TAG, "Connection Suspended");
        mGoogleApiClient.connect();
    }

    @Override
    public void onConnectionFailed(ConnectionResult connectionResult) {
        Log.i(TAG, "Connection failed. Error: " + connectionResult.getErrorCode());
    }

    // When app is started
    @Override
    protected void onStart() {
        super.onStart();

        // Start the Google API
        if (mGoogleApiClient != null) {
            mGoogleApiClient.connect();
        }
    }

    // Update the device's location (GPS Coordinates) in time
    protected void startLocationUpdates() {

        // Create the location request
        mLocationRequest = LocationRequest.create()
                .setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY)
                .setInterval(UPDATE_INTERVAL)
                .setFastestInterval(FASTEST_INTERVAL);

        // Check for the app's permissions
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {

            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_CONTACTS}, MY_PERMISSIONS_REQUEST_READ_FINE_LOCATION);
            return;
        }

        // Get the updated location of the device
        LocationServices.FusedLocationApi.requestLocationUpdates(mGoogleApiClient, mLocationRequest, this);

        Log.d("reque", "--->>>>");
    }

    // Location has changed
    @Override
    public void onLocationChanged(Location location) {

        Date currentTime = Calendar.getInstance().getTime();

        String msg = "Updated Location: " +
                Double.toString(location.getLatitude()) + "," +
                Double.toString(location.getLongitude()) + " | " + currentTime;


        // Set new latitude
        //mLatitudeTextView.setText(String.valueOf(location.getLatitude()));

        // Set new longitude
        //mLongitudeTextView.setText(String.valueOf(location.getLongitude() ));

        // Display pop up on screen with the values
        //Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();


        // LatLng Object can be created for use with maps
        LatLng latLng = new LatLng(location.getLatitude(), location.getLongitude());

        if (tx == null || msg == null || msg.isEmpty()) {
            // Do nothing if there is no device or message to send
        }

        else{

            tx = gatt.getService(UART_UUID).getCharacteristic(TX_UUID);

            tx.setValue(msg.getBytes(Charset.forName("UTF-8")));

            if (gatt.writeCharacteristic(tx)) {
                writeLine("App - " + msg);
            }
            else {
                writeLine("Could not write TX characteristic.");
            }
        }
    }

    // Check location
    private boolean checkLocation() {

        if(!isLocationEnabled())
            showAlert();
        return isLocationEnabled();
    }

    private void showAlert() {

        final AlertDialog.Builder dialog = new AlertDialog.Builder(this);
        dialog.setTitle("Enable Location")
                .setMessage("Your Locations Settings is set to 'Off'.\nPlease Enable Location to " +
                        "use this app")
                .setPositiveButton("Location Settings", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface paramDialogInterface, int paramInt) {

                        Intent myIntent = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                        startActivity(myIntent);
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface paramDialogInterface, int paramInt) {

                    }
                });
        dialog.show();
    }

    // Check if location is enabled
    private boolean isLocationEnabled() {

        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);

        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER);
    }


/*
# ------------------------------------------------------------------------------------ BLE Functions -------------------------------------------------------------------------------------------- #
*/

    // BLE device callbacks -> Handles the main logic of this class
    private BluetoothGattCallback callback = new BluetoothGattCallback() {

        // Function called whenever the device connection state changes -> from disconnected state to connected state
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {

            super.onConnectionStateChange(gatt, status, newState);

            String msgReady = "Ready";
            String msgEnd = "END";

            // Different states that can exist or change to
            if (newState == BluetoothGatt.STATE_CONNECTED) {

                writeLine("Connected to GATT Server - Sensing System");

                if (!gatt.discoverServices()) {

                    writeLine("Failed to start discovering services");
                }

            } else if (newState == BluetoothGatt.STATE_DISCONNECTED) {

                writeLine("Disconnected from GATT Server");

            } else {

                writeLine("Connection state changed.  New state: " + newState);
            }
        }

        // Function called when service have been discovered on the remote device (Raspberry Pi Zero)
        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {

            super.onServicesDiscovered(gatt, status);

            if (status == BluetoothGatt.GATT_SUCCESS) {
                writeLine("Sensing System Service discovery completed.");
            } else {
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

            } else {

                writeLine("Could not get RX client descriptor.");
            }
        }

        // Called when a remote characteristic changes -> like the RX characteristic
        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            /*
                Data received from the Raspberry Pi Zero
            */

            super.onCharacteristicChanged(gatt, characteristic);

            // Message received from the Raspberry Pi Zero
            String message = characteristic.getStringValue(0);

            // Call method to add the received data
            addData(message);

            populateDatabaseView();

            // Display on the Smartphone's screen
            writeLine("RPi Zero: " + characteristic.getStringValue(0));
        }
    };

    // BLE device scanning callback
    private LeScanCallback scanCallback = new LeScanCallback() {

        // Function called when the GATT Server (RPi Zero) is found
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
            writeLine("App - " + message);
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

    // Work around function from the SO thread to manually parse advertisement data
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
# ------------------------------------------------------------------------------- CAM Module Functions -------------------------------------------------------------------------------------------- #
*/

    // Check if the Message received from the Raspberry Pi is a CAM Message
    private void isCAM_Messages(String data){

    }

    // Save the CAM Message received from the Raspberry Pi Zero to the database
    public void addData(String newEntry){
        boolean insertData = mDatabase.addData(newEntry);

        if (insertData){
            System.out.println("Data successfully inserted!");
        }
        else{
            System.out.println("Data was not inserted on the data base. Something went wrong!");
        }
    }

    // Get the data presented on the database
    public void populateDatabaseView(){
        Log.d(TAG, "populateDatabaseView: Displaying data in the database");

        // Get the data and append to a list
        Cursor data = mDatabase.getData();
        ArrayList<String> listData = new ArrayList<>();
        while (data.moveToNext()){
            // Get the value from the database in column 1
            // then add it to the ArrayList
            listData.add(data.getString(1));
        }

        for (String el: listData){
            System.out.println(el);
        }
    }

    /*
    // Save the CAM Message received from the Raspberry Pi Zero to a text file
    private void saveCAM_Messages(String data) throws IOException {

        // Create buffer writer
        BufferedWriter bufferedWriter = null;

        String filePath = getApplicationContext().getFilesDir().getPath().toString() + "/camMessages.txt";

        // Create file
        File camFile = new File (filePath);

        // Check if file exists -> if not, create
        if (camFile.exists() == false){
            camFile.createNewFile();
            System.out.println("The CAM File has been created.");
        }
        else{
            System.out.println("The CAM File already exists.");
        }

        // Always write to a new line in the text file
        String myData = "\n" + data;

        try{
            // Save data to the text file -> append data in a new line to the file
            bufferedWriter = new BufferedWriter(new FileWriter(camFile, true));
            bufferedWriter.write(myData);

            System.out.println("CAM Message saved.");
        }
        catch (FileNotFoundException e){
            System.out.println("File not Found");
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }

     */

}
