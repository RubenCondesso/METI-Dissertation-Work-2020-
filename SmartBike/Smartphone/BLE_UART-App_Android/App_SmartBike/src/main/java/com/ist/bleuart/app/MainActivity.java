/*
#
# MainActivity.java - Java Class of Android App
#
# 7th May 2020 - 3.0
# 
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
# 
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
# 
# Java class that represents the main activity of the SmartBike's app
#
# Sends and receives data to a Bluetooth Low Energy UART service, which is running on the Raspberry Pi Zero (BLE GATT Server)
#
# Tracks the user's location in time -> GPS coordinates
#
# Stores some type of messages received from the Raspberry Pi Zero on a SQLite Database -> CAM Messages
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
import android.graphics.drawable.ColorDrawable;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.provider.Settings;
import android.text.Layout;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.Menu;

import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
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
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Scanner;
import java.util.TimeZone;
import java.util.UUID;

import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.app.ActivityCompat;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.maps.model.LatLng;

import java.util.Calendar;

/*
# ======================================================================================================================================================================================================================================================= #
# ==============================================================================================================    Functions    ======================================================================================================================== #
# ======================================================================================================================================================================================================================================================= #
*/

// Main Activity of the SmartBike's Application
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
    private static final String ADD = "Add Data to SQLite Database";
    private static final String RESULT = "DEN Message result";
    private static final String VALID = "CAM Message veracity";
    private static final String TYPE = "Message's type";

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

    // Time interval between location requests -> 5 seconds
    private long UPDATE_INTERVAL = 2 * 500;

    // Fastest time interval between location requests -> 1 second
    private long FASTEST_INTERVAL = 1000;

    private static final int MY_PERMISSIONS_REQUEST_READ_FINE_LOCATION = 100;

    // Initialize sql database
    SQLite_Database mDatabase;

    /**
     *  Called when the activity starts for the first time
     *  Initialize the needed methods and variables
     * @param savedInstanceState - Locale-specific object
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Keep the screen on
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        // check the user's permissions
        boolean permissionGranted = ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;

        if(permissionGranted) {
        } else {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, 200);
        }

        // Grab the references to the UI elements
        messages = (TextView) findViewById(R.id.messages);
        input = (EditText) findViewById(R.id.input);

        mDatabase = new SQLite_Database(this);

        // Clear database when app starts -> is optional
        mDatabase.clearDataBase("Data_table");

        adapter = BluetoothAdapter.getDefaultAdapter();

        //mLatitudeTextView = (TextView) findViewById((R.id.latitude_textview));
        //mLongitudeTextView = (TextView) findViewById((R.id.longitude_textview));

        mGoogleApiClient = new GoogleApiClient.Builder(this)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .build();

        mLocationManager = (LocationManager)this.getSystemService(Context.LOCATION_SERVICE);

        checkLocation();

    }

    /**
     *  Called right before UI is displayed
     *  Start the BLE connection
     */
    @Override
    protected void onResume() {

        super.onResume();

        // Scan for all BLE devices
        // The first one with the UART service (RPi Zero) will be chosen
        writeLine("Scanning for Bluetooth devices...");

        adapter.startLeScan(scanCallback);
    }

    /**
     *  Called right before the activity loses foreground focus
     *  Close the BLE connection
     */
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

    /**
     *  Check the user's permissions to this application -> Location
     */
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
# ================================================================================================================    GPS    ========================================================================================================================== #
*/

    /**
     *  Called  when the device is connected on the application
     *  Start checking the location of the Smartphone
     *  Check the application has the needed permissions
     * @param bundle - Locale-specific object
     */
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

        if (mLocation == null){

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

    /**
     *  Called  when the BLE connection is suspended
     */
    @Override
    public void onConnectionSuspended(int i) {
        Log.i(TAG, "Connection Suspended");
        mGoogleApiClient.connect();
    }

    /**
     *  Called  when the BLE connection failed
     * @param connectionResult - Result of the current connection
     */
    @Override
    public void onConnectionFailed(ConnectionResult connectionResult) {

        Log.i(TAG, "Connection failed. Error: " + connectionResult.getErrorCode());
    }

    /**
     *  Called  when the BLE connection starts
     */
    @Override
    protected void onStart() {

        super.onStart();

        // Start the Google API
        if (mGoogleApiClient != null) {
            mGoogleApiClient.connect();
        }
    }

    /**
     *  Update the device's location (GPS Coordinates) periodically (one second)
     */
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
    }

    /**
     *  Get the (current) changed location of the Smartphone
     *  Associate with the current timestamp
     *  Send new location to the Raspberry Pi Zero (GATT Server)
     * @param location - Location of the Smartphone
     */
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

    /**
     *  Check location
     * @return result of the check to the location
     */
    private boolean checkLocation() {

        if(!isLocationEnabled())
            showAlert();
        return isLocationEnabled();
    }

    /**
     *  Shows alerts
     */
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

    /**
     *  Check if the location is enabled
     * @return result of if location is enabled (or not)
     */
    private boolean isLocationEnabled() {

        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);

        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER);
    }


/*
# ================================================================================================================    BLE    ========================================================================================================================== #
*/

    /**
     *  BLE device callbacks -> Handles the main logic of this class
     */
    private BluetoothGattCallback callback = new BluetoothGattCallback() {

        /**
         *  Called whenever the device connection state changes -> from disconnected state to connected state
         * @param gatt - Object to the BLE Connection
         */
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {

            super.onConnectionStateChange(gatt, status, newState);

            String msgReady = "Ready";
            String msgEnd = "End";

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

        /**
         *  Called when UART Service have been discovered on the remote device (Raspberry Pi Zero -> GATT Server)
         *  @param gatt - Object to the BLE Connection
         */
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

        /**
         *  Called when a remote characteristic changes -> like the RX characteristic
         *  @param gatt - Object to the BLE Connection
         *  @param characteristic - Characteristic that changed
         */
        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            /*
                Data received from the Raspberry Pi Zero (GATT Server)
            */

            super.onCharacteristicChanged(gatt, characteristic);

            // Message received from the Raspberry Pi Zero
            String message = characteristic.getStringValue(0);

            // Check if is necessary to send a DEN Message
            try {
                boolean result = isDEN_Message();

                if (result){
                    Log.d(RESULT, "DEN Message will be sent -> an obstacle is to close to the user");

                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            // Pop up alert window
                            alertUser();
                        }
                    });
                }
                else{
                    Log.d(RESULT, "It is not necessary to a send DEN Message.");
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            // Check if the messages is the CAM's type
            if (isCAM_Message(message)){

                // Call method to add the received data
                addData(message);

                // Just for debug
                //populateDatabaseView();
            }

            // Display on the Smartphone's screen
            writeLine("RPi Zero: " + characteristic.getStringValue(0));
        }
    };

    /**
     *  BLE device scanning callback
     */
    private LeScanCallback scanCallback = new LeScanCallback() {

        /**
         *  Called when the Raspberry Pi Zero (GATT Server) is found
         *  @param bluetoothDevice - Bluetooth device present on the connection
         *
         */
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

    /**
     *  Handler for click on the send button
     *  @param view - Object that refers to action of clicking on button
     */
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

    /**
     * Write data to the messages text view
     * Care is taken to do this on the main UI thread so writeLine can be called from any thread (like the BLE callback)
     * @param text - Message that contains the data to be written
     */
    private void writeLine(final CharSequence text) {

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                messages.append(text);
                messages.append("\n");
            }
        });
    }

    /**
     * Work around function from the SO thread to manually parse advertisement data
     */
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

    /**
     * Boilerplate code from the activity creation
     * @param menu - Object that refers to menu of the SmartBike's application
     */
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {

        // Inflate the menu -> This adds items to the action bar if it is present
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

/*
# ==============================================================================================================    CAM Module    ======================================================================================================================== #
*/

    /**
     * Check if the Message received from the Raspberry Pi is a CAM's type of Message and if its a valid CAM message
     * @param data - String that refers to the message received
     * @return true if Message is CAM's type -> it has that exact structure: ID, Timestamp, Obstacle Distance, State and GPS Coordinates; and if all parameters are valid
     * @return false if not
     */
    private boolean isCAM_Message(String data){

        // Split string by spaces
        String[] splitStr = data.split("\\s+");

        // Check if message received has this exact structure
        if (splitStr[0].equals("ID:") || splitStr[3].equals("Timestamp:") || splitStr[9].equals("Obstacle") || splitStr[10].equals("distance:") || splitStr[13].equals("State:") || splitStr[16].equals("GPS") || splitStr[17].equals("Coordinates:")){

            System.out.println("Going to verify the veracity of the CAM Message" + "\n");

            // Check if all parameters are valid
            if (msgID_Veracity(splitStr[1]) && msgTimestamp_Veracity(splitStr[4], splitStr[5], splitStr[6]) && msgDistance_Veracity(splitStr[11]) && msgState_Veracity(splitStr[14]) && msgGPS_Veracity(splitStr[18])){

                Log.d(VALID, "CAM message received is valid!");

                return true;
            }
            else{

                Log.d(VALID, "CAM message received is not valid!");

                return false;
            }
        }

        Log.d(TYPE, "Message is not CAM's type!");

        return false;
    }

    /**
     * Check if the ID of the message received is valid
     * @param id - ID of the message received
     * @return true if message id is valid -> check if it has right format: X.X.X.X
     * @return false if not
     */
    private boolean msgID_Veracity(String id){

        char idChar = '.';
        int count = 0;

        for (int i = 0; i < id.length(); i ++){
            if(id.charAt(i) == idChar){
                count ++;
            }
        }
        // Id has to have three '.' to have the right format
        if (count == 3){
            return true;
        }
        else{
            return false;
        }
    }

    /**
     * Check if the timestamp of the message received is valid
     * @param day, month, year- timestamp of the message received
     * @return true if timestamp is valid -> check if it to old
     * @return false if not
     */
    private boolean msgTimestamp_Veracity(String day, String month, String year){

        // Current date
        Date now_date = new Date();

        // Choose time zone in which you wat to interpret your date
        Calendar cal = Calendar.getInstance(TimeZone.getTimeZone("Europe/Lisbon"));
        cal.setTime(now_date);

        // Current day
        int current_day = cal.get(Calendar.DAY_OF_MONTH);

        // Current month
        int current_month = (cal.get(Calendar.MONTH)) + 1;

        // Current year
        int current_year = cal.get(Calendar.YEAR);


        System.out.println("Month received: " + Integer.parseInt(month) + "\n");
        System.out.println("Current month: " + current_month + "\n");

        // Check timestamp of message received is too old
        if ((current_day == Integer.parseInt(day)) && (current_month == Integer.parseInt(month)) && (current_year == Integer.parseInt(year))){
            return true;
        }
        else {
            return false;
        }
    }

    /**
     * Check if the distance of the message received is valid
     * @param dist - distance of the message received
     * @return true if Message distance is valid -> check if it has right format: X.X
     * @return false if not
     */
    private boolean msgDistance_Veracity(String dist){

        char idChar = '.';
        int count = 0;

        for (int i = 0; i < dist.length(); i ++){
            if(dist.charAt(i) == idChar){
                count ++;
            }
        }
        // Id has to have one '.' to have the right format
        if (count == 1){
            return true;
        }
        else{
            return false;
        }
    }

    /**
     * Check if the state of the message received is valid
     * @param state - state of the message received
     * @return true if message state is valid -> check if it has right format: 'Immobile' || 'Moving'
     * @return false if not
     */
    private boolean msgState_Veracity(String state){

        String str1 = "Moving";
        String str2 = "Immobile";

        // State must be equal to one of the two possibilities
        if ((state.equals(str1) || (state.equals(str2)))){
            return true;
        }
        else{
            return false;
        }
    }

    /**
     * Check if the coordinates of the message received is valid
     * @param coords - distance of the message received
     * @return true if coordinates is valid -> check if it has right format: 'X.X,X.X'
     * @return false if not
     */
    private boolean msgGPS_Veracity(String coords){

        char gpsCharA = '.';
        char gpsCharB = ',';
        int countA = 0;
        int countB = 0;

        for (int i = 0; i < coords.length(); i ++) {
            if (coords.charAt(i) == gpsCharA) {
                countA++;
            }
            if (coords.charAt(i) == gpsCharB) {
                countB++;

            }
        }
        // Id has to have two '.' and one ',' to have the right format
        if (countA == 2 && countB == 1){
            return true;
        }
        else{
            return false;
        }
    }



    /**
     * Stores the CAM Message received from the Raspberry Pi Zero to the SQLite database
     * @param newEntry - Entry on the SQLite Database
     */
    public void addData(String newEntry){

        boolean insertData = mDatabase.addData(newEntry);

        if (insertData){
            Log.d(ADD, "Data successfully inserted!");
        }
        else{
            Log.d(ADD, "Data was not inserted on the data base. Something went wrong!");
        }
    }


/*
# ==============================================================================================================    DEN Module    ======================================================================================================================== #
*/

    /**
     * Check if DEN message is needed to be sent (and alert the user) -> An obstacle is very close to the user
     * @return true if distance to the obstacle is between 0 and 10 meters
     * @return false if not
     */
    private boolean isDEN_Message() throws InterruptedException {

        // Array with the distances to the obstacle presented in the SQLite Database
        ArrayList<String> result_distances = mDatabase.check_Distances();

        // Array with the obstacle's state presented in the SQLite Database
        ArrayList<String> result_state = mDatabase.check_State();

        for(int index = 0; index < result_distances.size(); index ++){

            String temp_state = result_state.get(index);

            // Check the state of the obstacle
            if (temp_state.equals("Moving")){

                // Convert string to float
                float dist = Float.valueOf(result_distances.get(index));

                // Check if distance is to close to the user
                if (dist > 0 && dist < 10){
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Alert the user about the proximity of an obstacle -> pop an alert dialog on the Smartphone
     */
    private void alertUser(){

        AlertDialog.Builder builder = new AlertDialog.Builder(MainActivity.this, R.style.AlertDialogTheme);
        View view = LayoutInflater.from(MainActivity.this).inflate(
                R.layout.layout_warning_dialog, (ConstraintLayout)findViewById(R.id.layoutDialogContainer)
        );
        builder.setView(view);
        ((TextView) view.findViewById(R.id.textTitle)).setText(getResources().getString(R.string.alert));
        ((TextView) view.findViewById(R.id.textMessage)).setText(getResources().getString(R.string.alertMsg));
        ((Button) view.findViewById(R.id.buttonAction)).setText(getResources().getString(R.string.ok));
        ((ImageView) view.findViewById(R.id.imageIcon)).setImageResource(R.drawable.ic_warning);

        final AlertDialog alertDialog = builder.create();
        view.findViewById(R.id.buttonAction).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                alertDialog.dismiss();
            }
        });

        if (alertDialog.getWindow() != null){
            alertDialog.getWindow().setBackgroundDrawable(new ColorDrawable(0));
        }
        alertDialog.show();
    }


/*
# ==============================================================================================================    Populate View    ======================================================================================================================== #
*/

    /**
     * Get the Data presented on the SQLite Database, in each column
     * For debug purposes
     */
    public void populateDatabaseView(){

        Log.d(TAG, "populateDatabaseView: Displaying data of the database");

        // Get the data and append to a list
        Cursor data = mDatabase.getData();

        ArrayList<String> listID = new ArrayList<>();
        ArrayList<String> listTime = new ArrayList<>();
        ArrayList<String> listDistance = new ArrayList<>();
        ArrayList<String> listState = new ArrayList<>();
        ArrayList<String> listGPS = new ArrayList<>();

        while (data.moveToNext()){
            // Get the value from the database in each column
            // then add it to the respective ArrayList
            listID.add(data.getString(1));
            listTime.add(data.getString(2));
            listDistance.add(data.getString(3));
            listState.add(data.getString(4));
            listGPS.add(data.getString(5));
        }

        for (String el: listID){
            System.out.println("Database - ID: " + el);
        }
        for (String el: listTime){
            System.out.println("Database - Timestamp: " + el);
        }
        for (String el: listDistance){
            System.out.println("Database - Distance: " + el);
        }
        for (String el: listState){
            System.out.println("Database - State: " + el);
        }
        for (String el: listGPS){
            System.out.println("Database - GPS: " + el);
        }
    }
}
