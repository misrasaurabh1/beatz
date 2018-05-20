import bokeh
import numpy as np
import librosa
import os
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool
import scipy.io
def hardcoded_segmenting(y):
    starts = np.array([4.845e3, 1.802e4, 3.143e4,4.495e4, 5.835e4, 7.151e4, 8.494e4, 9.814e4,
              1.116e5, 1.251e5, 1.383e5, 1.511e5, 1.644e5, 1.772e5, 1.910e5, 2.038e5,
              2.168e5, 2.300e5, 2.429e5, 2.564e5, 2.694e5 ])
    samples = 1024
    ends = starts + samples
    count = 0
    arr = np.zeros((len(starts),samples))
    for start, end in zip(starts,ends):
        arr[count] = y[int(start):int(end)]
        count +=1
    scipy.io.savemat("data/test/arr.mat",mdict={'arr':arr})
if __name__ == "__main__":
    files = {#'raw_dataset/snare_open_mouth.wav': "snare",
            'raw_dataset/snare_noisy_click.wav': "snare",
             #'raw_dataset/closedhihat_open_mouth1.wav': "closedhh",
             #'raw_dataset/kick_open_mouth1.wav': "kick",
             #'raw_dataset/openhihat_open_mouth1.wav': "openhh"
             }
    hover = HoverTool(tooltips=[
        ("x", "$x"),
        ("y", "$y")
    ])
    print(os.getcwd())
    for file in files:
        y, sr = librosa.load(file)
        y = np.multiply(y, 1 / y.max())
        clicks = np.linspace(4880,269500,21)
        print(clicks)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr,hop_length = 512,
        aggregate = np.median,centering=True)
        onset_env = np.multiply(onset_env,1/onset_env.max())
        onset_env_times = librosa.frames_to_samples(np.arange(len(onset_env)))
        print(len(y))
        print(len(onset_env))
        #onset_frames = librosa.util.peak_pick(onset_env,10,10,5,5,0.5,10)
        onset_frames = librosa.onset.onset_detect(y=y,backtrack=True)
        onsets = librosa.frames_to_samples(onset_frames)
        print(onsets)
        onset_frames_ontime = librosa.onset.onset_detect(y=y)
        onsets_t = librosa.frames_to_samples(onset_frames_ontime)
        p = figure(title="audio", x_axis_label="sample no.", y_axis_label='amplitude',
                   plot_width=30000, tools = [hover])
        p.line(np.arange(len(y)),y,line_width=1)
        p.line(onset_env_times,onset_env,line_width=1,line_color="blue")
        print(np.linspace(onset_env[0],onset_env[-1],len(onset_env)))

        #Reverse onset backtrack
        #oenv = librosa.onset.onset_strength(y=y, sr=sr)
        onset_raw = librosa.onset.onset_detect(onset_envelope=onset_env,backtrack = False)
        reversed_oenv = np.fliplr([onset_env])[0]

        last_frame = librosa.core.samples_to_frames([len(y)])[0]
        reversed_onsets = last_frame - onset_raw
        reversed_onsets = np.fliplr([reversed_onsets])[0]
        onset_bt_reversed = librosa.onset.onset_backtrack(reversed_onsets, reversed_oenv)
        onset_end = last_frame - onset_bt_reversed
        onset_end = librosa.core.frames_to_samples(onset_end)
        #beat tracker
        beat_times = librosa.beat.beat_track(y,start_bpm=100,units='samples')
        print(beat_times)
        #p.line(librosa.frames_to_samples(onset_env),onset_env)
        for onset in onsets:
            p.line([onset, onset], [0,0.5],line_color = "pink")
        #for onset in onsets_t:
        #    p.line([onset, onset], [0, 0.5], line_color="black")
        for click in clicks:
            p.line([click,click], [0,0.5], line_color = "red")
        for beat in beat_times[1]:

            p.line([beat,beat],[0,0.5], line_color = "black")
        for onset_last in onset_end:
            p.line([onset_last,onset_last], [0,0.5], line_color ="red")
        show(p)
        hardcoded_segmenting(y)
