from flask import Flask, request, send_file
import predict
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def hello_world():
    if request.method == "POST":
        print(request.files)
        f = request.files["test.wav"]
        f.save("/home/ubuntu/beatz/test_downloaded.wav")
        print(predict.predict("/home/ubuntu/beatz/test_downloaded.wav"))
        return send_file("/home/ubuntu/beatz/output.wav", as_attachment=True)
