from flask import send_file,Flask, flash, request, redirect, url_for
import predict
from label_new import label_files
from werkzeug.utils import secure_filename
import os.path
UPLOAD_FOLDER = '/home/ubuntu/beatz/data'
ALLOWED_EXTENSIONS = set(['mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#ypL"F4Q8z\n\xec]/'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/predict', methods=['POST'])
def hello_world():
    if request.method == "POST":
        print(request.files)
        f = request.files["test.wav"]
        f.save("/home/ubuntu/beatz/test_downloaded.wav")
        print(predict.predict("/home/ubuntu/beatz/test_downloaded.wav"))
        return send_file("/home/ubuntu/beatz/output.wav", as_attachment=True)

def save_train_file(request,instr):
    #print(request)
    print(request.files)
    if 'uploaded_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    args = request.args
    print(args)
    file = request.files['uploaded_file']
    print(request.files)
    print(file)
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        print("Entered allowed file")
        filename = secure_filename("upload_{}.mp4".format(instr))
        savePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(savePath)
        print("File saved!")
        return "upload_success", 200, savePath

@app.route('/uploadbass', methods=['POST'])
def save_bass():
    if request.method == "POST":
        ret = save_train_file(request, "bass")
        if len(ret) == 3 and ret[2]:
            label_files({ret[2]: "bass"})
        return ret[0], ret[1]

@app.route('/uploadsnare', methods=['POST'])
def save_snare():
    if request.method == "POST":
        ret = save_train_file(request, "snare")
        if len(ret) == 3 and ret[2]:
            label_files({ret[2]: "snare"})
        return ret[0], ret[1]

@app.route('/uploadclosedhh', methods=['POST'])
def save_hihat():
    if request.method == "POST":
        ret = save_train_file(request, "closedhh")
        if len(ret) == 3 and ret[2]:
            label_files({ret[2]: "closedhh"})
        return ret[0], ret[1]


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
