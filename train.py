import numpy as np
import os.path
import glob
import librosa
from collections import Counter
import sklearn
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib

from bokeh.plotting import figure, show


def loadSamples():
    data = []
    labels = []
    dirs = glob.glob("data/ver2/*/")
    for aDir in dirs:
        # data[os.path.basename(aDir)] = []
        npFiles = glob.glob(aDir + "/*.txt")
        for npFile in npFiles:
            arr = np.loadtxt(npFile)
            data.append(arr)
            aDir = aDir.rstrip('/')
            labels.append(os.path.basename(aDir))

    return data, labels


def extractFeatures(data, labels):
    features = []
    f_labels = []
    window_labels = []
    counter = 0
    for sample, label in zip(data, labels):
        mfcc = librosa.feature.mfcc(y=sample, sr=22050, n_mfcc=20)
        columns = np.hsplit(mfcc, mfcc.shape[1])
        window_labels += [counter] * len(columns)
        counter += len(columns)
        features = features + columns
        f_labels = f_labels + ([label] * mfcc.shape[1])
    return features, f_labels, window_labels


if __name__ == "__main__":
    X, Y = loadSamples()
    print(Counter(Y).most_common(4))
    X, Y, windows = extractFeatures(X, Y)
    print(Counter(Y).most_common(4))
    le = sklearn.preprocessing.LabelEncoder()
    data = np.array(X)
    data = data.reshape(data.shape[0], data.shape[1])
    scaler = sklearn.preprocessing.StandardScaler()
    data = scaler.fit_transform(data)
    joblib.dump(scaler, 'models/scaler.pkl')
    #data = sklearn.preprocessing.normalize(data, norm='l2')
    labels = le.fit_transform(Y)
    print(labels)
    print(data[2])
    shuf_data, shuf_labels = sklearn.utils.shuffle(data, labels)
    clf = sklearn.svm.SVC()

    scores = cross_val_score(clf, shuf_data, shuf_labels, cv=6)
    clf.fit(data, labels)
    print("Cross validation scores", scores)
    print("Cross-validation mean accuracy : {} (+- {})".format(scores.mean(), scores.std() * 2))
    train_predict_labels = clf.predict(data)
    print("training accuracy on whole dataset : {}".format(
        sklearn.metrics.accuracy_score(labels, train_predict_labels)))
    joblib.dump(clf, 'models/model.pkl')
    predict_windows ={}
    for w_idx, lbl in zip(windows, train_predict_labels):
        if w_idx in predict_windows:
            predict_windows[w_idx].append(lbl)
        else:
            predict_windows[w_idx] = [lbl]
    window_pred = []
    for window, pred_list in predict_windows.items():
        ctr = Counter(pred_list)
        window_pred.append([window,ctr.most_common(1)[0][0]])
    window_pred = sorted(window_pred, key=lambda val: val[0])

    preds = [l[1] for l in window_pred]
    pred_idx = [l[0] for l in window_pred]
    true_window_labels = labels[pred_idx]
    print("Window predictions accuracy {}".format(
        sklearn.metrics.accuracy_score(true_window_labels, preds)))
    anomaly = sklearn.svm.OneClassSVM()
    anomaly.fit(data)
    joblib.dump(anomaly, 'models/anomaly.pkl')
    pca = sklearn.decomposition.PCA(n_components=2)
    data_2d = pca.fit_transform(data)
    print(data_2d)
    colors = ["green", "gray", "red", "blue"] #
    label_colors = [colors[val] for val in labels]
    p = figure(plot_width=800, plot_height=800,)
    p.circle(data_2d[:,0], data_2d[:,1], size=5, color=label_colors)
    show(p)
