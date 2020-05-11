/*
#
# DataBase_CAM.java - Java Class of Android App
#
# 7th May 2020 - 1.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Java class that sets up the SQLite database to store the CAM messages (Periodically Messages) received from the Raspberry Pi Zero
#
#
# */


/*
# =================================================================================== Code starts here =====================================================================================#
*/


/*
# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #
*/

package com.ist.bleuart.app;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.AtomicFile;
import android.util.Log;

import androidx.annotation.Nullable;

import java.io.IOException;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.atomic.AtomicBoolean;


/*
# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #
*/

public class DataBase_CAM extends SQLiteOpenHelper {

    private static final String TAG = "CAMTABLE";
    private static final int DATABASE_VERSION = 2;
    private static final String TABLE_NAME = "CAM_table";
    private static final String KEY_MSG_ID = "ID";
    private static final String KEY_MSG_TEXT = "TEXT";

    /**
     *  Constructor
     * @param context - constructor of the SQLite Database
     */
    public DataBase_CAM(Context context) {
        super(context, TABLE_NAME, null, DATABASE_VERSION);
    }

    /**
     *  First time called, creates SQLite Database
     *  Creates the tables of the SQLite Database
     */
    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE " + TABLE_NAME + "(" + KEY_MSG_ID + " INTEGER PRIMARY KEY AUTOINCREMENT," + KEY_MSG_TEXT + " TEXT )");

        // Run Thread
        try {
            loadData();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    /**
     *  Check if sql database already exists, if so reset SQLite Database
     *  Called when upgrade is done
     * @param db - SQLite database
     */
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_NAME);
        onCreate(db);
    }

    /**
     *  Add data to the SQLite Database
     * @param item - data that contain MSG ID, Timestamp, Obstacle Distance, GPS coordinates
     * @return true if data is added
     */
    public boolean addData(String item){
        SQLiteDatabase db = this.getWritableDatabase();
        ContentValues contentValues = new ContentValues();
        contentValues.put(KEY_MSG_TEXT, item);

        Log.d(TAG, "addData: Adding -> " + item + " to " + TABLE_NAME);

        db.insert(TABLE_NAME, null, contentValues);
        db.close();
        return true;
    }

    /**
     *  Returns all the data from SQLite Database
     * @return data of the query
     */
    public Cursor getData(){

        SQLiteDatabase db = this.getWritableDatabase();
        String query = "SELECT * FROM " + TABLE_NAME;
        Cursor data = db.rawQuery(query, null);
        return data;
    }


    /**
     *  Set up Thread that constantly read the data presented on the SQLite CAM Database
     */
    public void loadData() throws InterruptedException {

        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                checkDEN();
            };
        });

        // Start thread
        t.start();
    }

    /**
     *  Constantly read the distances presented on the SQLite CAM Database
     *  If distances are to low (obstacle is to close to user), give alert -> DEN Message
     * @return true if is necessary to send DEN Message
     * @return false if is not
     */
    public boolean checkDEN(){

        Cursor data = getData();
        ArrayList<String> listData = new ArrayList<>();

        // Keyword -> Obstacle is on the move
        String keyword_State = "Moving";
        // Keyword -> Distance
        String keyword_Distance = "distance:";

        while (data.moveToNext()){
            // Get the value from the database in column 1 (data)
            // then add it to the ArrayList
            listData.add(data.getString(1));
        }
        for (String el: listData){
            Boolean stateObstacle = Arrays.asList(el.split(" ")).contains(keyword_State);

            if(stateObstacle){
                String obstacleDistance = getNextWord(el, keyword_Distance);

                if (obstacleDistance != null){

                    float distance = Float.parseFloat(obstacleDistance);
                    return check_Distance(distance);
                }
            }
        }
        return false;
    }

    /**
     * Get word after a specific word in a String
     * @return String if founded
     * @return Null if not
     */
    private static String getNextWord(String str, String word){

        String [] strArr = str.split(word);
        if(strArr.length > 1){
            strArr = strArr[1].trim().split(" ");
            return strArr[0];
        }
        return null;
    }

    /**
     * Check if a distance is too danger to the user
     * @return true if so
     * @return false if not
     */
    private static Boolean check_Distance(float distance){

        // Check if the obstacle is up to 5 meters at distance
        if (distance > 0 && distance < 5){
            return true;
        }
        return false;
    }
}
