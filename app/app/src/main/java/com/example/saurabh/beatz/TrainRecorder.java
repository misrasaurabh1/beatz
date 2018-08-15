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
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;
import android.support.v7.widget.AppCompatImageView;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class TrainRecorder extends AppCompatActivity {

    private static final String LOG_TAG = "AudioRecordTest";
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 200;
    private static String mFileName = null;
    private String mInstrument = null;
    private MediaRecorder mRecorder = null;

    private MediaPlayer   mPlayer = null;

    // Requesting permission to RECORD_AUDIO
    private boolean permissionToRecordAccepted = false;
    private String [] permissions = {Manifest.permission.RECORD_AUDIO};

    boolean mStartRecording = true;
    boolean mStartPlaying = true;

    private Map<String, String> mNextInstr = new HashMap<String, String>();
    public void initNextInstr(){
        mNextInstr.put("bass", "snare");
        mNextInstr.put("snare","hihat");
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode){
            case REQUEST_RECORD_AUDIO_PERMISSION:
                permissionToRecordAccepted  = grantResults[0] == PackageManager.PERMISSION_GRANTED;
                break;
        }
        if (!permissionToRecordAccepted ) finish();

    }

    private void onRecord(boolean start) {
        if (start) {
            startRecording();
        } else {
            stopRecording();
        }
    }

    private void onPlay(boolean start) {
        if (start) {
            startPlaying();
        } else {
            stopPlaying();
        }
    }

    private void startPlaying() {
        mPlayer = new MediaPlayer();
        try {
            mPlayer.setDataSource(mFileName);
            mPlayer.prepare();
            mPlayer.start();
        } catch (IOException e) {
            Log.e(LOG_TAG, "prepare() failed");
        }
    }

    private void stopPlaying() {
        mPlayer.release();
        mPlayer = null;
    }

    private void startRecording() {
        mRecorder = new MediaRecorder();
        mRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        mRecorder.setOutputFile(mFileName);
        mRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.HE_AAC);
        mRecorder.setAudioSamplingRate(44100);

        try {
            mRecorder.prepare();
        } catch (IOException e) {
            Log.e(LOG_TAG, "prepare() failed");
        }

        mRecorder.start();
    }

    private void stopRecording() {
        mRecorder.stop();
        mRecorder.release();
        mRecorder = null;
    }

    public void recordOnClick(View v){
        onRecord(mStartRecording);
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
        onPlay(mStartPlaying);
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
        intent.putExtra("filePath",mFileName);
        intent.putExtra("instrument", mInstrument);
        startService(intent);
        Toast.makeText(TrainRecorder.this, "File Upload started ",
                Toast.LENGTH_SHORT).show();
        Intent nextIntent = new Intent(this, TrainRecorder.class);
        String next =  mNextInstr.get(mInstrument);
        nextIntent.putExtra("Instrument_name", next);
        startActivity(nextIntent);
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
        mFileName += "/audiorecordtest.mp4";


        ActivityCompat.requestPermissions(this, permissions, REQUEST_RECORD_AUDIO_PERMISSION);

    }

    @Override
    public void onStop() {
        super.onStop();
        if (mRecorder != null) {
            mRecorder.release();
            mRecorder = null;
        }

        if (mPlayer != null) {
            mPlayer.release();
            mPlayer = null;
        }
    }
}