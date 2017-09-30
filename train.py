import numpy as np
import os.path
import glob
import librosa
from collections import Counter
import sklearn
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib
import cPickle
from bokeh.plotting import figure, show
def loadSamples():
	data = []
	labels = []
	dirs = glob.glob("data/*/")
	for aDir in dirs:
		#data[os.path.basename(aDir)] = []
		npFiles = glob.glob(aDir+"/*.txt")
		for npFile in npFiles:
			arr = np.loadtxt(npFile)
			data.append(arr)
			aDir = aDir.rstrip('/')
			labels.append(os.path.basename(aDir))

	return data, labels

def extractFeatures(data, labels):
	features = []
	f_labels = []
	for sample, label in zip(data,labels):
		mfcc = librosa.feature.mfcc(y= sample, sr= 22050, n_mfcc=20)
		columns = np.hsplit(mfcc,mfcc.shape[1])
		features = features +columns
		f_labels = f_labels + ([label] * mfcc.shape[1])
		
	return features, f_labels
if __name__ == "__main__":
	X, Y = loadSamples()
	print Counter(Y).most_common(4)
	X, Y = extractFeatures(X,Y)
	print Counter(Y).most_common(4)
	le = sklearn.preprocessing.LabelEncoder()
	data = np.array(X)
	data = data.reshape(data.shape[0],data.shape[1])
	data = sklearn.preprocessing.normalize(data, norm='l2')
	labels = le.fit_transform(Y)
	print labels
	print data[2]
	data, labels = sklearn.utils.shuffle(data,labels)
	clf = sklearn.svm.SVC()

	scores = cross_val_score(clf, data, labels, cv=6)
	clf.fit(data,labels)
	print "Cross validation scores",scores
	print "Cross-validation mean accuracy : {} (+- {})".format(scores.mean(), scores.std() *2)
	train_predict_labels = clf.predict(data)
	print "training accuracy on whole dataset : {}".format(
		sklearn.metrics.accuracy_score(labels, train_predict_labels))
	joblib.dump(clf, 'models/model.pkl')

	anomaly = sklearn.svm.OneClassSVM()
	anomaly.fit(data)
	joblib.dump(anomaly, 'models/anomaly.pkl')
	pca = sklearn.decomposition.PCA(n_components = 2)
	data_2d = pca.fit_transform(data)
	print data_2d

	p = figure(plot_width=800, plot_height=800)
	p.circle(zip(*data_2d)[0], zip(*data_2d)[1]	,size=5)
	show(p)