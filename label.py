from librosa import load
import bokeh
import numpy as np
import os.path
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool
from math import sqrt
from sklearn.cluster import DBSCAN
rms_window = 60
openhh_threshold = 3.0e-3
drawGraph = 1
if __name__ == "__main__":
	hover = HoverTool(tooltips=[
			    ("x", "$x"),
			    ("y", "$y")
			])
	#for closedhithat_open_mouth1.wav, remove x = 5.466e+5 sample
	files = {'raw_dataset/snare_open_mouth.wav' : "snare",
			#'raw_dataset/closedhihat_open_mouth1.wav' : "closedhh",
			#'raw_dataset/kick_open_mouth1.wav' : "kick",
			#'raw_dataset/openhihat_open_mouth1.wav' : "openhh"
			}
	for file in files:
		y, sr = load(file, sr= 22050)
		y = np.multiply(y, 1/y.max())
		y = np.pad(y,(rms_window,rms_window), 'constant', constant_values=(0,0))

		inst_power = np.zeros(len(y))

		for start_idx in xrange(0,len(y)- rms_window/2 -1):
			inst_power[start_idx + rms_window/2] = sqrt(np.sum(np.square(y[start_idx:(start_idx+rms_window)]))) /rms_window
		index = 0
		if files[file] == "openhh":
			avg_power = openhh_threshold
		else:
			avg_power = np.average(inst_power) * 3.8
		print "avg_power", avg_power
		segments = []
		while index < len(inst_power):
			if inst_power[index] >avg_power:
				temp_index = index
				while inst_power[temp_index-1]< inst_power[temp_index]:
					temp_index -= 1
				start = temp_index
				while inst_power[index] > avg_power and index <len(inst_power):
					index += 1
				temp_index = index
				while inst_power[temp_index+1] < inst_power[temp_index]:
					temp_index +=1
				end = temp_index
				segments.append([start,end])
			else:
				index += 1
		segments_flat = [[item] for sublist in segments for item in sublist]
		dbscan = DBSCAN(eps=5000, min_samples=2)
		cluster_labels = dbscan.fit_predict(segments_flat)
		print "file {} num samples determined {}".format(file, max(cluster_labels))
		pointsMap = {}
		for idx, point in enumerate(cluster_labels):
			if point in pointsMap:
				pointsMap[point].append(idx)
			else:
				pointsMap[point] = [idx]
		pointsMap.pop(-1,None)
		#print pointsMap
		maxEnergySeg = {}
		for key in pointsMap:
			assert(len(pointsMap[key]) %2 ==0),"Odd number of elements in key {}!".format(key)

			for points in pointsMap[key]:
				if points %2 ==1:
					continue
				cur_segment = segments[points/2]
				energy = np.sum(np.square(y[cur_segment[0]:cur_segment[1]]))
				if key in maxEnergySeg:
					if energy > maxEnergySeg[key]['energy']:
						maxEnergySeg[key]['energy'] = energy
						maxEnergySeg[key]['pos'] = points/2
				else:
					maxEnergySeg[key]={}
					maxEnergySeg[key]['energy'] = energy
					maxEnergySeg[key]['pos'] = points/2

		if(drawGraph):
			
			#output_file("plots/{}.html".format(file))
			p = figure(title="audio",x_axis_label = "sample no.", y_axis_label = 'amplitude', plot_width = 30000 )#tools = [hover])

			#p.line(np.arange(len(y)), y, line_width =1 )
			p.line(np.arange(len(inst_power)), inst_power , line_width = 1)
			mx = inst_power.max()
			mn = inst_power.min()
			matches = []
			for seg in maxEnergySeg:
				couple = segments[maxEnergySeg[seg]['pos']]
				matches.append(couple)
				p.line([couple[0], couple[0]], [mn,mx], line_color = "green")
				p.line([couple[1], couple[1]], [mn,mx], line_color = "red")
			p.line(np.arange(len(inst_power)), avg_power, line_width = 1, line_color = "red")
			show(p)

		for idx,seg in enumerate(maxEnergySeg):
			seg_start, seg_stop = segments[maxEnergySeg[seg]['pos']]
			np.savetxt(os.path.join('data',files[file], str(idx)+'.txt'),y[seg_start:seg_stop], fmt = '%f')