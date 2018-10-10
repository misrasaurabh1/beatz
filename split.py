import scipy.io.wavfile
from glob import glob
import os
import matplotlib
from bokeh.plotting import figure, show
import numpy as np

topPath = os.path.dirname(os.path.realpath(__file__))
rate = 0
data = []
for file in glob(os.path.join(topPath, 'dataset/*.wav')):
	rate_file, data_file = scipy.io.wavfile.read(file)
	if(rate == 0):
		rate = rate_file
	else:
		assert(rate == rate_file)

	data_file = np.array([sum(x)/2.0 for x in data_file])
	data.append(data_file)

p = figure(width = 1000, height = 1000, title= "one wav file",x_axis_label="time", y_axis_label="sound")
p.line(np.linspace(0, 1, len(data[0])), data[0])
show(p)
