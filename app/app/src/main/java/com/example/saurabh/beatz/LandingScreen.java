package com.example.saurabh.beatz;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;

public class LandingScreen extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_landing_screen);
    }

    public void onTrainerClick(View v){
        Intent intent = new Intent(getBaseContext(), TrainRecorder.class);
        intent.putExtra("Instrument_name", "bass");
        startActivity(intent);
    }
}
