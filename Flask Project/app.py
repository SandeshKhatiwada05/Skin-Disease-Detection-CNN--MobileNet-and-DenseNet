import os
import uuid
import pymysql
from datetime import datetime
from flask import (
    Flask, abort, render_template, request,
    redirect, url_for, flash, session
)
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array

app = Flask(__name__)
app.secret_key = 'protect_sessions_and_cookies123'

# Paths
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database connection
db = pymysql.connect(
    host="localhost",
    user="root",
    password="admin",
    database="skin_disease_db",
    cursorclass=pymysql.cursors.DictCursor
)
cursor = db.cursor()

# Model
MODEL_PATH = os.path.join(app.root_path, 'DenseNetMadeInkaggle.h5')
if not os.path.isfile(MODEL_PATH):
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
model = load_model(MODEL_PATH)

# Allowed formats
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'jfif'}

def is_allowed(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Class labels (order matters)
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

def get_prediction(image_path: str):
    """Return top 4 classes and their probabilities (%)"""
    img = load_img(image_path, target_size=(224, 224))
    arr = img_to_array(img)
    # NOTE: Your original training likely used preprocess_input; you currently divide by 255.0 implicitly
    # If you want closer alignment to original DenseNet preprocessing, import and use preprocess_input.
    arr = arr.reshape(1, 224, 224, 3).astype('float32') / 255.0
    probs = model.predict(arr, verbose=0)[0]
    labeled = list(zip(class_labels, probs))
    labeled.sort(key=lambda x: x[1], reverse=True)
    top = labeled[:4]
    top_classes = [c for c, _ in top]
    top_probs = [round(p * 100.0, 2) for _, p in top]
    return top_classes, top_probs

def get_prediction_count(user_id: int) -> int:
    cursor.execute("SELECT COUNT(*) AS cnt FROM predictions WHERE user_id=%s", (user_id,))
    row = cursor.fetchone()
    return row['cnt'] if row else 0

# Make username & prediction count available to every template
@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        return {
            'current_username': session.get('username'),
            'prediction_count': get_prediction_count(user_id)
        }
    return {
        'current_username': None,
        'prediction_count': 0
    }

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash("Provide both username and password.")
            return render_template('login.html')

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!')
            return redirect(url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        pw = request.form.get('password', '')
        cpw = request.form.get('confirm_password', '')

        if not username or not pw or not cpw:
            flash("All fields are required.")
            return render_template('register.html')

        if pw != cpw:
            flash("Passwords do not match.")
            return render_template('register.html')

        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            flash("Username already taken.")
            return render_template('register.html')

        password_hash = generate_password_hash(pw)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
            (username, password_hash)
        )
        db.commit()
        flash("Account created. Please login.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('login'))

@app.route('/success', methods=['POST'])
def success():
    if 'user_id' not in session:
        flash('Please login.')
        return redirect(url_for('login'))

    if 'file' not in request.files:
        return render_template('index.html', error='No file part.')

    file = request.files['file']
    if not file.filename:
        return render_template('index.html', error='No file selected.')

    if not is_allowed(file.filename):
        return render_template('index.html', error='Only jpg, jpeg, png, jfif formats are accepted.')

    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(save_path)

    top_classes, top_probs = get_prediction(save_path)

    cursor.execute(
        "INSERT INTO predictions (user_id, image_filename, prediction_text, prediction_date) "
        "VALUES (%s,%s,%s,%s)",
        (session['user_id'], unique_name, top_classes[0], datetime.now())
    )
    db.commit()

    results = {
        'class1': top_classes[0], 'prob1': top_probs[0],
        'class2': top_classes[1], 'prob2': top_probs[1],
        'class3': top_classes[2], 'prob3': top_probs[2],
        'class4': top_classes[3], 'prob4': top_probs[3],
    }
    return render_template('success.html', img=unique_name, predictions=results)

@app.route('/pastrecords')
def pastrecords():
    if 'user_id' not in session:
        flash('Please login.')
        return redirect(url_for('login'))
    cursor.execute(
        "SELECT * FROM predictions WHERE user_id=%s ORDER BY prediction_date DESC",
        (session['user_id'],)
    )
    records = cursor.fetchall()
    return render_template('pastrecords.html', records=records)

@app.route('/delete_record/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    if 'user_id' not in session:
        flash('Please login.')
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM predictions WHERE id=%s", (record_id,))
    rec = cursor.fetchone()
    if not rec or rec['user_id'] != session['user_id']:
        abort(403)

    cursor.execute("DELETE FROM predictions WHERE id=%s", (record_id,))
    db.commit()
    flash('Record deleted.')
    return redirect(url_for('pastrecords'))

if __name__ == '__main__':
    app.run(debug=True, port=4000)