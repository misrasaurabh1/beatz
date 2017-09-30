import sklearn
import librosa
import argparse
import numpy as np
import sklearn
from math import sqrt
from bokeh.plotting import figure,show
seek_distance = 256
rms_window = 60
snare_file = "samples/shortlists/snare/CYCdh_K1close_Snr-05-16bit.wav"
kick_file = "samples/shortlists/kick/CYCdh_AcouKick-10-16bit.wav"
closedhh_file = "samples/shortlists/closedhh/CYCdh_K4-ClHat02-16bit.wav"
openhh_file = "samples/shortlists/openhh/KHatsOpen-07-16bit.wav"

parser = argparse.ArgumentParser()
parser.add_argument("file", help ="path of the wav file to predict")
args = parser.parse_args()

y,sr = librosa.load(args.file, sr=22050)
y = np.multiply(y, 1/y.max())
#y = np.pad(y,(rms_window/2,rms_window/2), 'constant', constant_values=(0,0))

onset_samples = librosa.onset.onset_detect(y=y, sr=sr, units='samples',hop_length =256)
inst_power = np.zeros(len(y))
for start_idx in xrange(0,len(y)- rms_window/2 -1):
	inst_power[start_idx + rms_window/2] = sqrt(np.sum(np.square(y[start_idx:(start_idx+rms_window)]))) /rms_window
p = figure(plot_width=1900)
p.line(np.arange(len(inst_power)),inst_power)
for sample in onset_samples:
	p.line([sample,sample],[0.0,max(inst_power)],color="red")
show(p)
detected_events = []
for center in onset_samples:
	detected_events.append(np.array([center - seek_distance +1, center + seek_distance]))
print("detected_events :{}".format(len(detected_events)))
windows = []
#print detected_events
for event in detected_events:
	print(event)
	mfcc = librosa.feature.mfcc(y = y[event[0]: event[1]], sr=sr, n_mfcc=20)
	columns = np.hsplit(mfcc,mfcc.shape[1])
	windows = windows +columns
windows =np.array(windows)
windows = windows.reshape(windows.shape[0],windows.shape[1])
print(windows.shape)
windows = sklearn.preprocessing.normalize(windows, norm='l2')
anomaly = sklearn.externals.joblib.load('models/anomaly.pkl')
print(anomaly.predict(windows))

clf = sklearn.externals.joblib.load('models/model.pkl')
predict = clf.predict(windows)
print(predict)
out_sr = 44100
snare,_ = librosa.load(snare_file, sr = out_sr)
openhh,_ = librosa.load(openhh_file, sr = out_sr)
kick,_ = librosa.load(kick_file, sr = out_sr)
closedhh,_ = librosa.load(closedhh_file, sr = out_sr)

out_audio = np.zeros(len(y)*2)
for idx, event_time in enumerate(onset_samples):
	event_time *=2
	pred = predict[idx]
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
	print event_time, len(current_sample)
	if event_time+len(current_sample)> len(out_audio):
		current_sample = current_sample[:len(out_audio)-event_time-1]
	out_audio[event_time:event_time+len(current_sample)] += current_sample

librosa.output.write_wav("output.wav", out_audio, sr= out_sr, norm=True) 
#Windowing to use similar method as used for labelling. Energy based segmentation