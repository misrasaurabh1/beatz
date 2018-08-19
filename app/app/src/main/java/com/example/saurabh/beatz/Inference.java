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

public class Inference extends AppCompatActivity{
    String mFileName;
    Media media;
    boolean mStartRecording = true;
    boolean mStartPlaying = true;
    // Requesting permission to RECORD_AUDIO
    private boolean permissionToRecordAccepted = false;
    private String [] permissions = {Manifest.permission.RECORD_AUDIO};
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 200;

    @Override
    public void onCreate(Bundle icicle) {
        super.onCreate(icicle);
        setContentView(R.layout.activity_inference);
        TextView instrText = (TextView) findViewById(R.id.instrumentText);
        // Record to the external cache directory for visibility
        mFileName = getExternalCacheDir().getAbsolutePath();
        mFileName += "audio.mp4";
        media = new Media(mFileName);

        ActivityCompat.requestPermissions(this, permissions, REQUEST_RECORD_AUDIO_PERMISSION);

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
            Intent intent = new Intent(this, UploaderService.class);
            intent.putExtra("filePath",mFileName);
            intent.putExtra("instrument", "predict");
            startService(intent);
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

}
