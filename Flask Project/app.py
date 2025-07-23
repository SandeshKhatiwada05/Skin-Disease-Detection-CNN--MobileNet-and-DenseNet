import os
import uuid
import urllib.request
from flask import Flask, render_template, request
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the trained DenseNet model
MODEL_PATH = os.path.join(app.root_path, 'densenetv2.h5')
model = load_model(MODEL_PATH)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'jfif'}

def is_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Class names matching the DenseNet output
class_labels = [
    'Actinic keratosis',
    'Atopic Dermatitis',
    'Benign keratosis',
    'Dermatofibroma',
    'Melanocytic nevus',
    'Melanoma',
    'Squamous cell carcinoma',
    'Tinea Ringworm Candidiasis',
    'Vascular lesion'
]

# Wikipedia or trusted links for each disease
wiki_links = {
    'Actinic keratosis': 'https://en.wikipedia.org/wiki/Actinic_keratosis',
    'Atopic Dermatitis': 'https://en.wikipedia.org/wiki/Atopic_dermatitis',
    'Benign keratosis': 'https://en.wikipedia.org/wiki/Seborrheic_keratosis',
    'Dermatofibroma': 'https://en.wikipedia.org/wiki/Dermatofibroma',
    'Melanocytic nevus': 'https://en.wikipedia.org/wiki/Melanocytic_nevus',
    'Melanoma': 'https://en.wikipedia.org/wiki/Melanoma',
    'Squamous cell carcinoma': 'https://en.wikipedia.org/wiki/Squamous_cell_carcinoma',
    'Tinea Ringworm Candidiasis': 'https://en.wikipedia.org/wiki/Tinea',
    'Vascular lesion': 'https://neurosurgerywiki.com/wiki/doku.php?id=vascular_lesion'
}

def get_prediction(image_path):
    # Resize to 240x240 as model expects
    img = load_img(image_path, target_size=(240, 240))
    img_arr = img_to_array(img)
    img_arr = img_arr.reshape(1, 240, 240, 3).astype('float32') / 255.0

    predictions = model.predict(img_arr)[0]
    pred_with_labels = list(zip(class_labels, predictions))
    pred_with_labels.sort(key=lambda x: x[1], reverse=True)

    top_preds = pred_with_labels[:4]
    top_classes = [label for label, prob in top_preds]
    top_probs = [(prob * 100).round(2) for label, prob in top_preds]

    return top_classes, top_probs

@app.route('/')
def home():
    return render_template('index.html')

# ... your existing code above unchanged ...

@app.route('/success', methods=['POST'])
def success():
    error_msg = ''

    if request.form.get('link'):
        image_url = request.form.get('link')
        try:
            response = urllib.request.urlopen(image_url)
            unique_name = f"{uuid.uuid4()}.jpg"
            saved_path = os.path.join(UPLOAD_FOLDER, unique_name)
            with open(saved_path, 'wb') as f:
                f.write(response.read())

            top_classes, top_probs = get_prediction(saved_path)

            results = {
                'class1': top_classes[0], 'prob1': top_probs[0], 'url1': wiki_links.get(top_classes[0], '#'),
                'class2': top_classes[1], 'prob2': top_probs[1], 'url2': wiki_links.get(top_classes[1], '#'),
                'class3': top_classes[2], 'prob3': top_probs[2], 'url3': wiki_links.get(top_classes[2], '#'),
                'class4': top_classes[3], 'prob4': top_probs[3], 'url4': wiki_links.get(top_classes[3], '#'),
            }
            return render_template('success.html', img=unique_name, predictions=results)

        except Exception as e:
            print(str(e))
            error_msg = "Unable to fetch or process image from the provided URL."

    elif 'file' in request.files:
        image_file = request.files['file']

        if image_file and is_allowed(image_file.filename):
            filename = image_file.filename
            saved_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(saved_path)

            top_classes, top_probs = get_prediction(saved_path)

            results = {
                'class1': top_classes[0], 'prob1': top_probs[0], 'url1': wiki_links.get(top_classes[0], '#'),
                'class2': top_classes[1], 'prob2': top_probs[1], 'url2': wiki_links.get(top_classes[1], '#'),
                'class3': top_classes[2], 'prob3': top_probs[2], 'url3': wiki_links.get(top_classes[2], '#'),
                'class4': top_classes[3], 'prob4': top_probs[3], 'url4': wiki_links.get(top_classes[3], '#'),
            }
            return render_template('success.html', img=filename, predictions=results)
        else:
            error_msg = "Only jpg, jpeg, png, jfif formats are accepted."

    return render_template('index.html', error=error_msg)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
