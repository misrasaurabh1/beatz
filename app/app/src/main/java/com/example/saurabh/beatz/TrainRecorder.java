//package com.example.saurabh.beatz;
//
//import android.support.v7.app.AppCompatActivity;
//import android.os.Bundle;
//
//public class LandingScreen extends AppCompatActivity {
//
//    @Override
//    protected void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//        setContentView(R.layout.activity_landing_screen);
//    }
//}

package com.example.saurabh.beatz;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

public class TrainRecorder extends AppCompatActivity {

    private static final String LOG_TAG = "AudioRecordTest";
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 200;
    private static String mFileName = null;
    private String mInstrument = null;
    Media media;
    // Requesting permission to RECORD_AUDIO
    private boolean permissionToRecordAccepted = false;
    private String [] permissions = {Manifest.permission.RECORD_AUDIO};

    boolean mStartRecording = true;
    boolean mStartPlaying = true;

    private Map<String, String> mNextInstr = new HashMap<String, String>();

    public void initNextInstr(){
        mNextInstr.put("bass", "snare");
        mNextInstr.put("snare","closedhh");
    }


    public void recordOnClick(View v){
        media.onRecord(mStartRecording);
        ImageView img = (ImageView) findViewById(R.id.recordButton);
        if (mStartRecording) {

            img.setImageResource(R.drawable.ic_stop);
            //setText("Stop recording");
        } else {
            //setText("Start recording");
            img.setImageResource(R.drawable.ic_microphone);
            ImageView play = (ImageView) findViewById(R.id.playButton);
            play.setVisibility(View.VISIBLE);
            Button nextBtn = (Button) findViewById(R.id.btnNext);
            nextBtn.setVisibility(View.VISIBLE);
        }
        mStartRecording = !mStartRecording;
    }

    public void playOnClick(View v){
        media.onPlay(mStartPlaying);
        ImageView img = (ImageView) findViewById(R.id.playButton);
        if (mStartPlaying) {
            img.setImageResource(R.drawable.ic_stop);
            //setText("Stop playing");
        } else {
            img.setImageResource(R.drawable.ic_play);
            //setText("Start playing");
        }
        mStartPlaying = !mStartPlaying;
    }

    public void nextButtonClick(View v){
        Intent intent = new Intent(this, UploaderService.class);
        File f = new File(mFileName);
        intent.putExtra("filePath",mFileName);
        intent.putExtra("instrument", mInstrument);
        startService(intent);
        if(mInstrument.equals("closedhh")){
            Toast.makeText(TrainRecorder.this, "Uploading and learning",
                    Toast.LENGTH_SHORT).show();
            Intent homeIntent = new Intent(this, LandingScreen.class);
            startActivity(homeIntent);
        }
        else {
            Toast.makeText(TrainRecorder.this, "File Upload started ",
                    Toast.LENGTH_SHORT).show();
            Intent nextIntent = new Intent(this, TrainRecorder.class);
            String next = mNextInstr.get(mInstrument);
            nextIntent.putExtra("Instrument_name", next);
            startActivity(nextIntent);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode) {
            case REQUEST_RECORD_AUDIO_PERMISSION:
                permissionToRecordAccepted = grantResults[0] == PackageManager.PERMISSION_GRANTED;
                break;
        }
        if (!permissionToRecordAccepted) finish();

    }
    @Override
    public void onCreate(Bundle icicle) {
        super.onCreate(icicle);
        setContentView(R.layout.activity_train_record);
        initNextInstr();
        String instrument= getIntent().getStringExtra("Instrument_name");
        TextView instrText = (TextView) findViewById(R.id.instrumentText);
        instrText.setText(instrument);
        mInstrument = instrument;
        // Record to the external cache directory for visibility
        mFileName = getExternalCacheDir().getAbsolutePath();
        mFileName += "audio.mp4";
        media = new Media(mFileName);
        ActivityCompat.requestPermissions(this, permissions, REQUEST_RECORD_AUDIO_PERMISSION);

    }

    @Override
    public void onStop() {
        super.onStop();
        media.onStopAction();
    }
}