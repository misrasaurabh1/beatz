import librosa
import librosa.display
import numpy as np
# Get onset times from a signal
def onset():
	y, sr = librosa.load('raw_dataset/test-clip.wav')
	onset_frames = librosa.onset.onset_detect(y=y, sr=sr,units='samples')
	librosa.frames_to_time(onset_frames, sr=sr)
	# array([ 0.07 ,  0.395,  0.511,  0.627,  0.766,  0.975,
	# 1.207,  1.324,  1.44 ,  1.788,  1.881])

	# Or use a pre-computed onset envelope

	o_env = librosa.onset.onset_strength(y, sr=sr)
	print "len onset strength :{}".format(len(o_env))
	times = librosa.frames_to_time(np.arange(len(o_env)), sr=sr)
	onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr)

	import matplotlib.pyplot as plt
	D = librosa.stft(y)
	plt.figure()
	ax1 = plt.subplot(2, 1, 1)
	librosa.display.specshow(librosa.amplitude_to_db(D, ref=np.max),x_axis='time', y_axis='log')
	plt.title('Power spectrogram')
	plt.subplot(2, 1, 2, sharex=ax1)
	plt.plot(times, o_env, label='Onset strength')
	plt.vlines(times[onset_frames], 0, o_env.max(), color='r', alpha=0.9,
	           linestyle='--', label='Onsets')
	plt.axis('tight')
	plt.legend(frameon=True, framealpha=0.75)
	plt.show()

def harmonicPercussivePlot():
	y,sr = librosa.load('raw_dataset/snare_open_mouth.wav', duration =10)
	D = librosa.stft(y)
	H, P = librosa.decompose.hpss(D)
	import matplotlib.pyplot as plt
	plt.figure()
	plt.subplot(3, 1, 1)
	librosa.display.specshow(librosa.amplitude_to_db(D,ref=np.max),y_axis='log')
	librosa.display.specshow(librosa.amplitude_to_db(D,ref=np.max),y_axis='log')
	plt.colorbar(format='%+2.0f dB')
	plt.title('Full power spectrogram')
	plt.subplot(3, 1, 2)
	librosa.display.specshow(librosa.amplitude_to_db(H,ref=np.max),y_axis='log')
	plt.colorbar(format='%+2.0f dB')
	plt.title('Harmonic power spectrogram')
	plt.subplot(3, 1, 3)
	librosa.display.specshow(librosa.amplitude_to_db(P,ref=np.max),y_axis='log')
	plt.colorbar(format='%+2.0f dB')
	plt.title('Percussive power spectrogram')
	plt.tight_layout()
	plt.show()
	p =librosa.istft(P)
	librosa.output.write_wav('test.wav',p, sr=sr)

#harmonicPercussivePlot()
onset()