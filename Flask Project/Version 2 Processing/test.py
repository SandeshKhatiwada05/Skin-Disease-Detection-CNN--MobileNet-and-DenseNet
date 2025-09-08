import pytest
from refactored import app, is_allowed, external_url_for, predict_image, CLASS_NAMES
from flask import url_for

# ------------------------------
# Helper function tests
# ------------------------------

def test_is_allowed_valid():
    assert is_allowed("image.jpg")
    assert is_allowed("photo.jpeg")
    assert is_allowed("scan.png")
    assert is_allowed("skin.jfif")

def test_is_allowed_invalid():
    assert not is_allowed("file.gif")
    assert not is_allowed("notes.txt")
    assert not is_allowed("data.pdf")

# ------------------------------
# External URL tests
# ------------------------------

def test_external_url_known():
    url = external_url_for("acne")
    # "acne" not in EXTERNAL_INFO, so fallback Google search is used
    assert "google.com/search" in url.lower()

def test_external_url_unknown():
    url = external_url_for("randomdisease")
    assert "google.com/search" in url.lower()

# ------------------------------
# Predict image test (mock model)
# ------------------------------

def test_predict_image_mock(monkeypatch, tmp_path):
    """Monkeypatch get_model to avoid loading real DenseNet model."""
    import numpy as np
    from PIL import Image
    from refactored import get_model

    class DummyModel:
        def predict(self, arr, verbose=0):
            # 9 classes → return fake probs as NumPy array
            return np.array([[0.1, 0.2, 0.05, 0.05, 0.05, 0.25, 0.1, 0.05, 0.05]])

    monkeypatch.setattr("refactored.get_model", lambda: DummyModel())

    # create a fake image
    img_path = tmp_path / "test.png"
    Image.new("RGB", (224, 224), color="white").save(img_path)

    pred = predict_image(str(img_path))
    assert isinstance(pred, dict)
    assert "primary_label" in pred
    assert "top" in pred
    assert "max_prob" in pred

# ------------------------------
# Flask client tests
# ------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_redirects_if_not_logged_in(client):
    response = client.get("/")
    assert response.status_code == 302  # redirect
    assert "/login" in response.headers["Location"]

def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200
    # Check title contains 'Sign up' as in your template
    assert b"Sign up" in response.data
