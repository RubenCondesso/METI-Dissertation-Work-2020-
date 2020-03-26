/*
#
# LocationRepository.java - Java Class of Android App
#
# 25 March 2020 - 1.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Creates the services/actions on the the Data Base (room)  -> it stores the user's coordinates in time
#
# */


/*
# =================================================================================== Code starts here ===================================================================================== #
*/


/*
# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #
*/


package com.ist.bleuart.app;

import android.content.Context;
import android.os.AsyncTask;
import androidx.lifecycle.LiveData;
import androidx.room.Room;
import java.util.List;


/*
# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #
*/

// Data Base
public class LocationRepository {
    private String DB_NAME = "location_db";
    private MyDataBase myDataBase;

    // Create the room
    public LocationRepository(Context context) {
        myDataBase = Room.databaseBuilder(context, MyDataBase.class, DB_NAME).build();
    }

    // insert a new location in the data base
    public void insertLocation(final MyLocation location) {
        new AsyncTask<Void, Void, Void>() {
            @Override
            protected Void doInBackground(Void... voids) {
                myDataBase.dao().insertLocation(location);
                return null;
            }
        }.execute();
    }

    // update a location in the data base
    public void updateLocation(final MyLocation location) {

        new AsyncTask<Void, Void, Void>() {
            @Override
            protected Void doInBackground(Void... voids) {
                myDataBase.dao().updateLocation(location);
                return null;
            }
        }.execute();
    }

    // delete a location in the data base
    public void deleteLocation(final int id) {
        final LiveData<MyLocation> location = getLocation(id);
        if (location != null) {
            new AsyncTask<Void, Void, Void>() {
                @Override
                protected Void doInBackground(Void... voids) {
                    myDataBase.dao().deleteLocation(location.getValue());
                    return null;
                }
            }.execute();
        }
    }

    // delete a location in the data base
    public void deleteLocation(final MyLocation location) {
        new AsyncTask<Void, Void, Void>() {
            @Override
            protected Void doInBackground(Void... voids) {
                myDataBase.dao().deleteLocation(location);
                return null;
            }
        }.execute();
    }

    // get a location in the data base
    public LiveData<MyLocation> getLocation(int id) {
        return myDataBase.dao().getLocation(id);
    }

    public LiveData<List<MyLocation>> getLocations() {
        return myDataBase.dao().fetchAllLocation();
    }
}