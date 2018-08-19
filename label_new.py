import bokeh
import numpy as np
import librosa
import os
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool
import scipy.io
from sklearn.cluster import DBSCAN
import sys
debug = False
files = {#'raw_dataset/snare_open_mouth.wav': "snare",
             'raw_dataset/click/snare_noisy_click.wav': "snare",
             'raw_dataset/click/closedhh-click.wav': "closedhh",
             'raw_dataset/click/kick-click.wav': "kick",
             'raw_dataset/click/openhh-click.wav': "openhh"
             }
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
def get_clicks(instr):
    if(instr == "snare"):
        clicks = np.linspace(4880, 269500, 21)
    if(instr == "kick"):
        clicks = np.linspace(3421, 453300, 35)
    return clicks
def segments_wrt_clicks(onsets,onset_end,cluster_labels):
    dbscan = DBSCAN(eps=4000, min_samples=2)
    concat_array = np.concatenate((onsets, onset_end))
    concat_array = concat_array.reshape(concat_array.shape[0], 1)
    print(concat_array.shape)
    cluster_labels = dbscan.fit_predict(concat_array)
    len_onsets = len(onsets)
    segments = np.zeros((min(len(onset_end), len(onsets)), 2))

    for idx, label in enumerate(cluster_labels):
        pos_2 = 0
        if (idx >= len_onsets):
            pos_2 = 1
        segments[label, pos_2] = concat_array[idx]
    segments_cleaned = []
    for segment in segments:
        skip = 1
        for click in clicks:
            if abs(segment[0] - click) < distance_limit:
                skip = 0
                break;
        if skip == 1:
            continue
        segments_cleaned.append([segment[0], segment[1]])

    print(segments_cleaned)
    return segments_cleaned

def segments_beat_tracking(beats, onsets, onset_end):
    segments_cleaned=[]
    for beat in beats:
        onset_sub = onsets - beat
        onset_end_sub = onset_end - beat
        closest_onset = onset_sub[np.where(onset_sub <0)[0]].max()
        closest_onset_end = onset_end_sub[np.where(onset_end_sub > 0)].min()
        if(closest_onset> -4000 and closest_onset_end <4000):
            segments_cleaned.append([closest_onset + beat, closest_onset_end + beat])

    return segments_cleaned

def label_files(files, debug = False):
    if debug:
        hover = HoverTool(tooltips=[
            ("x", "$x"),
            ("y", "$y")
        ])
    print(os.getcwd())
    hop_dist = 256
    for file in files:
        y, sr = librosa.load(file)
        y = np.multiply(y, 1 / y.max())
        if(files[file] == "openhh"):
            hop_dist = 512
        distance_limit = 1500
        plot_debug = 1
        #clicks = get_clicks(files[file])
        onset_env = librosa.onset.onset_strength(y=y, sr=sr,hop_length = hop_dist,
            aggregate = np.median,centering=True)
        onset_env = np.multiply(onset_env, 1/onset_env.max())
        onset_env_times = librosa.frames_to_samples(np.arange(len(onset_env)),hop_length=hop_dist)
        print(len(y))
        print(len(onset_env))
        #onset_frames = librosa.util.peak_pick(onset_env,10,10,5,5,0.5,10)
        onset_frames = librosa.onset.onset_detect(y=y, backtrack=True, hop_length=hop_dist)
        onsets = librosa.frames_to_samples(onset_frames, hop_length=hop_dist)
        print(onsets)
        onset_frames_ontime = librosa.onset.onset_detect(onset_envelope=onset_env)
        onsets_t = librosa.frames_to_samples(onset_frames_ontime, hop_length=hop_dist)
        if debug:
            p = figure(title="audio", x_axis_label="sample no.", y_axis_label='amplitude',
                       plot_width=30000, tools = [hover])
            p.line(np.arange(len(y)), y,line_width=1)
            p.line(onset_env_times,onset_env,line_width=1,line_color="blue")

            print(np.linspace(onset_env[0],onset_env[-1],len(onset_env)))

        #Reverse onset backtrack
        #oenv = librosa.onset.onset_strength(y=y, sr=sr)
        onset_raw = librosa.onset.onset_detect(onset_envelope=onset_env,backtrack=False,hop_length=hop_dist)
        reversed_oenv = np.fliplr([onset_env])[0]

        last_frame = librosa.core.samples_to_frames([len(y)], hop_length=hop_dist)[0]
        reversed_onsets = last_frame - onset_raw
        reversed_onsets = np.fliplr([reversed_onsets])[0]
        onset_bt_reversed = librosa.onset.onset_backtrack(reversed_onsets, reversed_oenv)
        onset_end = last_frame - onset_bt_reversed
        onset_end = librosa.core.frames_to_samples(onset_end, hop_length=hop_dist)
        #beat tracker
        beat_times = librosa.beat.beat_track(y,start_bpm=100,units='samples')
        print("Beat times")
        print(beat_times)

        # for onset in onsets:
        #     p.line([onset, onset], [0,0.5],line_color = "pink")
        #for onset in onsets_t:
        #    p.line([onset, onset], [0, 0.5], line_color="black")
        # for click in clicks:
        #     p.line([click,click], [0,0.5], line_color = "red")
        # for beat in beat_times[1]:
        #
        #     p.line([beat,beat],[0,0.5], line_color = "black")
        # for onset_last in onset_end:
        #     p.line([onset_last,onset_last], [0,0.5], line_color ="red")
        #show(p)


        #segments_cleaned = segments_wrt_clicks(onsets,onset_end,cluster_labels)
        segments_cleaned = segments_beat_tracking(beat_times[1],onsets,onset_end)
        print(len(segments_cleaned))
        path = os.path.join('data', files[file])
        if not os.path.isdir(path):
            os.mkdir(path)
        for idx, segment in enumerate(segments_cleaned):
            if debug:
                p.line([segment[0], segment[0]], [0,0.5], line_color="green")
                p.line([segment[1], segment[1]], [0,0.5], line_color="green")
            np.savetxt(os.path.join(path, str(idx) + '.txt'), y[int(segment[0]):int(segment[1])], fmt='%f')
        if debug:
            show(p)

        #hardcoded_segmenting(y)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        debug = True
    label_files(files, debug)