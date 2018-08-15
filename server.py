from flask import send_file,Flask, flash, request, redirect, url_for
import predict
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

@app.route('/uploadbass', methods=['POST'])
def train_file():
    if request.method == "POST":
        print(request)
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
            filename = secure_filename("uploadbass.mp4")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("File saved!")
            return "upload_success", 200
