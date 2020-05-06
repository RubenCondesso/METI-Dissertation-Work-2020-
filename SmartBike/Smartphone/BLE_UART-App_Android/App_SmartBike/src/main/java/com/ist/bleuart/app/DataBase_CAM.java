package com.ist.bleuart.app;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;

import androidx.annotation.Nullable;

public class DataBase_CAM extends SQLiteOpenHelper {

    private static final String TAG = "CAMTABLE";
    private static final int DATABASE_VERSION = 2;
    private static final String TABLE_NAME = "CAM_table";
    private static final String KEY_MSG_ID = "ID";
    private static final String KEY_MSG_TEXT = "TEXT";

    public DataBase_CAM(Context context) {
        super(context, TABLE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE " + TABLE_NAME + "(" + KEY_MSG_ID + " INTEGER PRIMARY KEY AUTOINCREMENT," + KEY_MSG_TEXT + " TEXT )");
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_NAME);
        onCreate(db);
    }

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
     *  Returns all the data from database
     * @return
     */
    public Cursor getData(){
        SQLiteDatabase db = this.getWritableDatabase();
        String query = "SELECT * FROM " + TABLE_NAME;
        Cursor data = db.rawQuery(query, null);
        return data;
    }
}
