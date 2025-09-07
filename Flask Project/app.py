import os
import uuid
import urllib.request
import pymysql
from datetime import datetime
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'protect_sessions_and_cookies123'

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection using pymysql
db = pymysql.connect(
    host="localhost",
    user="root",
    password="admin",  
    database="skin_disease_db",
    cursorclass=pymysql.cursors.DictCursor
)
cursor = db.cursor()

# Load the trained DenseNet model
MODEL_PATH = os.path.join(app.root_path, 'DenseNet_81PercentageAccuracy.h5')
model = load_model(MODEL_PATH)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'jfif'}

def is_allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Disease class labels
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

def get_prediction(image_path):
    img = load_img(image_path, target_size=(224, 224))  # Fix size here
    img_arr = img_to_array(img)
    img_arr = img_arr.reshape(1, 224, 224, 3).astype('float32') / 255.0  # Fix size here too

    predictions = model.predict(img_arr)[0]
    pred_with_labels = list(zip(class_labels, predictions))
    pred_with_labels.sort(key=lambda x: x[1], reverse=True)

    top_preds = pred_with_labels[:4]
    top_classes = [label for label, prob in top_preds]
    top_probs = [(prob * 100).round(2) for label, prob in top_preds]

    return top_classes, top_probs

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not password or not confirm_password:
            flash("All fields are required.")
            return render_template('register.html')

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template('register.html')

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Username already taken.")
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        db.commit()
        flash("Account created successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/success', methods=['POST'])
def success():
    if 'user_id' not in session:
        flash('Please login to use this feature.')
        return redirect(url_for('login'))

    error_msg = ''

    if 'file' in request.files:
        image_file = request.files['file']

        if image_file and is_allowed(image_file.filename):
            ext = image_file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4()}.{ext}"
            saved_path = os.path.join(UPLOAD_FOLDER, unique_name)
            image_file.save(saved_path)

            top_classes, top_probs = get_prediction(saved_path)

            now = datetime.now()
            cursor.execute(
                "INSERT INTO predictions (user_id, image_filename, prediction_text, prediction_date) VALUES (%s, %s, %s, %s)",
                (session['user_id'], unique_name, top_classes[0], now)
            )
            db.commit()

            results = {
                'class1': top_classes[0], 'prob1': top_probs[0],
                'class2': top_classes[1], 'prob2': top_probs[1],
                'class3': top_classes[2], 'prob3': top_probs[2],
                'class4': top_classes[3], 'prob4': top_probs[3],
            }
            return render_template('success.html', img=unique_name, predictions=results)
        else:
            error_msg = "Only jpg, jpeg, png, jfif formats are accepted."
    else:
        error_msg = "No file part in the request."

    return render_template('index.html', error=error_msg)

@app.route('/pastrecords')
def pastrecords():
    if 'user_id' not in session:
        flash('Please login to view past records.')
        return redirect(url_for('login'))

    cursor.execute(
        "SELECT * FROM predictions WHERE user_id = %s ORDER BY prediction_date DESC",
        (session['user_id'],)
    )
    records = cursor.fetchall()
    return render_template('pastrecords.html', records=records)

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    if 'user_id' not in session:
        flash('Please login to perform this action.')
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM predictions WHERE id = %s", (record_id,))
    record = cursor.fetchone()

    if not record or record['user_id'] != session['user_id']:
        abort(403)  # Forbidden

    cursor.execute("DELETE FROM predictions WHERE id = %s", (record_id,))
    db.commit()

    flash('Record deleted successfully.')
    return redirect(url_for('pastrecords'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)
