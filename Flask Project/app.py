from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER = os.path.join('static', 'images')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success', methods=['POST'])
def success():
    if 'file' not in request.files:
        return render_template('index.html', error="No file part in the form!")

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error="No file selected!")

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Dummy prediction data (replace with your model predictions if you want)
    predictions = {
        'class1': 'Benign', 'prob1': 92,
        'class2': 'Malignant', 'prob2': 5,
        'class3': 'Uncertain', 'prob3': 2,
        'class4': 'Other', 'prob4': 1,
    }

    return render_template('success.html', img=file.filename, predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True)
