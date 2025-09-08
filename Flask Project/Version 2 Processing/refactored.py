# refactored.py
import os
import uuid
from datetime import datetime

import pymysql
from flask import (
    Flask, abort, render_template, request,
    redirect, url_for, flash, session
)
from werkzeug.security import generate_password_hash, check_password_hash

from tensorflow.keras.models import load_model
from tensorflow.keras.utils import load_img, img_to_array
from tensorflow.keras.applications.densenet import preprocess_input

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_FILE = os.path.join(BASE_DIR, "DenseNet_81PercentageAccuracy.h5")

STATIC_IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")
os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)

CLASS_NAMES = [
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

DEFAULT_OPEN_SET_THRESHOLD = 0.50
OPEN_SET_THRESHOLD = float(os.environ.get("OPEN_SET_THRESHOLD", DEFAULT_OPEN_SET_THRESHOLD))
UNKNOWN_LABEL = "Undetectable / Outside Supported Classes"

EXTERNAL_INFO = {
    'actinic keratosis': 'https://dermnetnz.org/topics/actinic-keratosis',
    'atopic dermatitis': 'https://dermnetnz.org/topics/atopic-dermatitis',
    'benign keratosis': 'https://dermnetnz.org/topics/seborrhoeic-keratoses',
    'dermatofibroma': 'https://dermnetnz.org/topics/dermatofibroma',
    'melanocytic nevus': 'https://dermnetnz.org/topics/melanocytic-naevi-of-the-skin',
    'melanoma': 'https://dermnetnz.org/topics/melanoma',
    'squamous cell carcinoma': 'https://dermnetnz.org/topics/cutaneous-squamous-cell-carcinoma',
    'tinea ringworm candidiasis': 'https://dermnetnz.org/topics/tinea-corporis',
    'vascular lesion': 'https://dermnetnz.org/search?query=vascular%20lesion'
}

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'jfif'}

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
app.secret_key = "protect_sessions_and_cookies123"

# ============================================================
# DATABASE
# ============================================================

db = pymysql.connect(
    host="localhost",
    user="root",
    password="admin",
    database="skin_disease_db",
    cursorclass=pymysql.cursors.DictCursor
)
cursor = db.cursor()

# ============================================================
# MODEL LOADING (Lazy Initialization)
# ============================================================

_model = None  # private global

def get_model():
    """Load model lazily and cache it."""
    global _model
    if _model is None:
        if not os.path.isfile(MODEL_FILE):
            raise FileNotFoundError(f"Model file not found: {MODEL_FILE}")
        print(f"[INFO] Loading model from: {MODEL_FILE}")
        _model = load_model(MODEL_FILE)
        print(f"[INFO] Model loaded. Open-set threshold = {OPEN_SET_THRESHOLD:.3f}")
    return _model

# ============================================================
# HELPERS
# ============================================================

def is_allowed(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def external_url_for(name: str) -> str:
    key = (name or "").strip().lower()
    return EXTERNAL_INFO.get(
        key,
        f"https://www.google.com/search?q=site:dermnetnz.org+{key.replace(' ', '+')}"
    )

def predict_image(image_path: str, top_k: int = 4):
    model = get_model()
    img = load_img(image_path, target_size=(224, 224))
    arr = img_to_array(img)
    arr = arr.reshape(1, 224, 224, 3)
    arr = preprocess_input(arr)

    probs = model.predict(arr, verbose=0)[0]  # softmax
    max_prob = float(probs.max())
    max_idx = int(probs.argmax())
    is_unknown = max_prob < OPEN_SET_THRESHOLD

    sorted_idx = probs.argsort()[::-1]
    top_pairs = [(CLASS_NAMES[i], float(probs[i]) * 100.0) for i in sorted_idx[:top_k]]

    return {
        "unknown": is_unknown,
        "primary_label": UNKNOWN_LABEL if is_unknown else CLASS_NAMES[max_idx],
        "max_prob": max_prob * 100.0,
        "threshold": OPEN_SET_THRESHOLD * 100.0,
        "top": top_pairs
    }

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Login successful.")
            return redirect(url_for("home"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        cpw = request.form.get("confirm_password", "")

        if not username or not pw or not cpw:
            flash("All fields required.")
            return render_template("register.html")
        if pw != cpw:
            flash("Passwords do not match.")
            return render_template("register.html")

        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            flash("Username already taken.")
            return render_template("register.html")

        password_hash = generate_password_hash(pw)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
            (username, password_hash)
        )
        db.commit()
        flash("Account created. Please login.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("login"))

@app.route("/success", methods=["POST"])
def success():
    if 'user_id' not in session:
        flash("Please login.")
        return redirect(url_for("login"))

    if 'file' not in request.files:
        return render_template("index.html", error="No file part.")
    file = request.files['file']
    if not file.filename:
        return render_template("index.html", error="No file selected.")
    if not is_allowed(file.filename):
        return render_template("index.html", error="Only jpg, jpeg, png, jfif allowed.")

    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(STATIC_IMAGES_DIR, unique_name)
    file.save(save_path)

    pred = predict_image(save_path, top_k=4)

    # Store main (could be Undetectable)
    cursor.execute(
        "INSERT INTO predictions (user_id, image_filename, prediction_text, prediction_date) VALUES (%s,%s,%s,%s)",
        (session['user_id'], unique_name, pred['primary_label'], datetime.now())
    )
    db.commit()

    # Build template dictionary
    if pred['unknown']:
        predictions = {
            'is_unknown': True,
            'undetectable_label': "Undetectable (Outside Trained Scope)",
            'undetectable_prob': round(pred['max_prob'], 2),
            'threshold': round(pred['threshold'], 2),
            'max_prob': round(pred['max_prob'], 2),
            'primary': pred['primary_label']
        }
    else:
        top_entries = pred['top']
        while len(top_entries) < 4:
            top_entries.append(('', 0.0))

        predictions = {
            'is_unknown': False,
            'class1': top_entries[0][0], 'prob1': round(top_entries[0][1], 2), 'url1': external_url_for(top_entries[0][0]) if top_entries[0][0] else '',
            'class2': top_entries[1][0], 'prob2': round(top_entries[1][1], 2), 'url2': external_url_for(top_entries[1][0]) if top_entries[1][0] else '',
            'class3': top_entries[2][0], 'prob3': round(top_entries[2][1], 2), 'url3': external_url_for(top_entries[2][0]) if top_entries[2][0] else '',
            'class4': top_entries[3][0], 'prob4': round(top_entries[3][1], 2), 'url4': external_url_for(top_entries[3][0]) if top_entries[3][0] else '',
            'primary': pred['primary_label'],
            'max_prob': round(pred['max_prob'], 2),
            'threshold': round(pred['threshold'], 2)
        }

    return render_template("success.html", img=unique_name, predictions=predictions)

@app.route("/pastrecords")
def pastrecords():
    if 'user_id' not in session:
        flash("Please login.")
        return redirect(url_for("login"))
    cursor.execute("SELECT * FROM predictions WHERE user_id=%s ORDER BY prediction_date DESC", (session['user_id'],))
    rows = cursor.fetchall()
    return render_template("pastrecords.html", records=rows)

@app.route("/delete_record/<int:record_id>", methods=['POST'])
def delete_record(record_id):
    if 'user_id' not in session:
        flash("Please login.")
        return redirect(url_for("login"))
    cursor.execute("SELECT * FROM predictions WHERE id=%s", (record_id,))
    rec = cursor.fetchone()
    if not rec or rec['user_id'] != session['user_id']:
        abort(403)
    cursor.execute("DELETE FROM predictions WHERE id=%s", (record_id,))
    db.commit()
    flash("Record deleted.")
    return redirect(url_for("pastrecords"))

if __name__ == "__main__":
    print(f"[INFO] Starting app with model: {MODEL_FILE}")
    # preload model here if you want startup load
    get_model()
    app.run(debug=True, port=4000)

# ------------------------------------------------------------
# EXPORTS (so tests can import these)
# ------------------------------------------------------------
__all__ = [
    "app",
    "is_allowed",
    "external_url_for",
    "predict_image",
    "CLASS_NAMES",
    "UNKNOWN_LABEL",
    "get_model"
]

