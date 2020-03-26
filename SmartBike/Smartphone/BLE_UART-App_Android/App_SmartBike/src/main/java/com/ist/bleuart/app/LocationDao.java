/*
#
# LocationDao.java - Java Class of Android App
#
# 25 March 2020 - 1.0
#
# Author: Ruben Condesso - 81969 - 2nd Semester (2020)
#
#
# SmartBike System - Master Thesis in Telecommunications and Computer Engineering
#
#
# Allows to read and write on the data base
#
# */


/*
# =================================================================================== Code starts here =====================================================================================#
*/


/*
# -------------------------------------------------------------------------------------- Libraries ----------------------------------------------------------------------------------------- #
*/


package com.ist.bleuart.app;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Insert;
import androidx.room.Query;
import androidx.room.Update;
import java.util.List;


/*
# -------------------------------------------------------------------------------------- Functions ------------------------------------------------------------------------------------------ #
*/

// Location Dao
@Dao
public interface LocationDao {

    @Insert
    Long insertLocation(MyLocation location);


    @Query("SELECT * FROM MyLocation")
    LiveData<List<MyLocation>> fetchAllLocation();


    @Query("SELECT * FROM MyLocation WHERE id =:id")
    LiveData<MyLocation> getLocation(int id);


    @Update
    void updateLocation(MyLocation location);


    @Delete
    void deleteLocation(MyLocation location);
}