import sklearn
import librosa
import argparse
import numpy as np
import sklearn
from collections import Counter
from bokeh.plotting import figure,show
from Bio import pairwise2
from Bio.pairwise2 import format_alignment
seek_distance = 256
rms_window = 60
snare_file = "samples/shortlists/snare/CYCdh_K1close_Snr-05-16bit.wav"
kick_file = "samples/shortlists/kick/CYCdh_AcouKick-10-16bit.wav"
closedhh_file = "samples/shortlists/closedhh/CYCdh_K4-ClHat02-16bit.wav"
openhh_file = "samples/shortlists/openhh/KHatsOpen-07-16bit.wav"

def get_windows(y,sr):
    hop_dist = 256
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_dist,
                                             aggregate=np.median, centering=True)
    onset_env = np.multiply(onset_env, 1 / onset_env.max())
    onset_frames = librosa.onset.onset_detect(y=y, backtrack=True, hop_length=hop_dist)
    onsets = librosa.frames_to_samples(onset_frames, hop_length=hop_dist)
    reversed_oenv = np.fliplr([onset_env])[0]
    last_frame = librosa.core.samples_to_frames([len(y)], hop_length=hop_dist)[0]
    onset_raw = librosa.onset.onset_detect(onset_envelope=onset_env, backtrack=False, hop_length=hop_dist)
    reversed_onsets = last_frame - onset_raw
    reversed_onsets = np.fliplr([reversed_onsets])[0]
    onset_bt_reversed = librosa.onset.onset_backtrack(reversed_onsets, reversed_oenv)
    onset_end = last_frame - onset_bt_reversed
    onset_end = librosa.core.frames_to_samples(onset_end, hop_length=hop_dist)
    onset_end = np.flip(onset_end, axis=0)
    return onsets, onset_end


def predict(file):

    true_op = "12321232123212321232121301232123012321213012321130121321221233"


    y, sr = librosa.load(file, sr=22050)
    y = np.multiply(y, 1/y.max())
    #y = np.pad(y,(rms_window/2,rms_window/2), 'constant', constant_values=(0,0))

    onset_samples = librosa.onset.onset_detect(y=y, sr=sr, units='samples', hop_length=256)
    print(onset_samples)
    windows_start, windows_end = get_windows(y, 22050)
    # inst_power = np.zeros(len(y))
    # for start_idx in range(0, len(y) - rms_window//2 - 1):
    #     inst_power[start_idx + rms_window//2] = sqrt(np.sum(np.square(y[start_idx:(start_idx+rms_window)]))) //rms_window
    p = figure(plot_width=1900)
    p.line(np.arange(len(y)), y)
    for start, end in zip(windows_start,windows_end):
        p.line([start,start],[0.0,0.8], color="green")
        p.line([end, end], [0.0, 0.8], color="red")
    show(p)
    #detected_events = []
    # for center in onset_samples:
    #     detected_events.append(np.array([center - seek_distance//2 +1, center + 3*seek_distance//2]))
    # print("detected_events :{}".format(len(detected_events)))
    windows = []
    #print detected_events
    window_idx = []
    counter = 0
    for start, end in zip(windows_start, windows_end):
        print(start, end)
        mfcc = librosa.feature.mfcc(y=y[start: end], sr=sr, n_mfcc=20)
        columns = np.hsplit(mfcc, mfcc.shape[1])
        window_idx.append([counter, counter + len(columns)])
        counter += len(columns)
        windows += columns
    #windows = np.ndarray(windows)
    #windows = windows.reshape(windows.shape[0], windows.shape[1])
    for i in range(len(windows)):
        windows[i] = windows[i].reshape(windows[i].shape[0])
    print(windows[0].shape)
    scaler = sklearn.externals.joblib.load('models/scaler.pkl')
    windows = scaler.transform(windows)
    #windows = sklearn.preprocessing.normalize(windows, norm='l2')
    anomaly = sklearn.externals.joblib.load('models/anomaly.pkl')
    print(anomaly.predict(windows))

    clf = sklearn.externals.joblib.load('models/model.pkl')
    predict = clf.predict(windows)
    predict_windows =[]
    for start, end in window_idx:
        ctr = Counter(predict[start:end])
        predict_windows.append(ctr.most_common(1)[0][0])
    pred_str = "".join([str(x) for x in predict_windows])
    alignments = pairwise2.align.globalxx(true_op, pred_str)
    print(format_alignment(*alignments[0]))
    out_sr = 44100
    snare,_ = librosa.load(snare_file, sr=out_sr)
    openhh,_ = librosa.load(openhh_file, sr=out_sr)
    kick,_ = librosa.load(kick_file, sr=out_sr)
    closedhh,_ = librosa.load(closedhh_file, sr=out_sr)

    out_audio = np.zeros(len(y)*2)
    for idx, event_time in enumerate(onset_samples):
        event_time *= 2
        pred = predict_windows[idx]
        if pred == 1:
            current_sample = kick
        elif pred == 2:
            current_sample = closedhh
        elif pred == 3:
            current_sample = snare
        elif pred == 0:
            current_sample = openhh
        else:
            print("Wrong predicted category")
            continue
        print(event_time, len(current_sample))
        if event_time+len(current_sample)> len(out_audio):
            current_sample = current_sample[:len(out_audio)-event_time-1]
        out_audio[event_time:event_time+len(current_sample)] += current_sample

    input_resample = librosa.resample(y, 22050, out_sr)
    out_joined = out_audio + input_resample
    librosa.output.write_wav("output.wav", out_audio, sr=out_sr, norm=True)
    librosa.output.write_wav("output_joined.wav", out_joined, sr=out_sr, norm=True)
    p_joined = figure(plot_width = 25000)
    p_joined.line(np.arange(len(input_resample)), input_resample, color="green")
    p_joined.line(np.arange(len(input_resample)), out_audio, color="red")
    show(p_joined)
    #Windowing to use similar method as used for labelling. Energy based segmentation
    return "output.wav"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="path of the wav file to predict")
    args = parser.parse_args()
    predict(args.file)
