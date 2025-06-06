echo "# 🧠 AI for Skin Disease Detection

A multi-class skin disease classifier using CNN, DenseNet121, and MobileNetV1 on the DermNet dataset.

---

## 📌 Project Overview

This project applies deep learning to dermatology by classifying 9 common skin diseases using image data. It compares performance across a custom CNN, MobileNetV1, and DenseNet121 using TensorFlow and Keras.

---

## ✅ Current Features

- ✅ Data preprocessing from the DermNet dataset  
- ✅ Custom CNN model implemented from scratch  
- ✅ Transfer learning with MobileNetV1  
- ✅ Transfer learning with DenseNet121  
- ✅ Training, validation, and testing splits  
- ✅ Accuracy & loss visualization using Seaborn  
- ✅ Confusion matrix evaluation using Scikit-plot  

---

## 🗂️ Dataset

- 📁 **Source**: https://www.kaggle.com/datasets/shubhamgoel27/dermnet  
- 🖼️ **Classes**: 9 skin conditions (Melanoma, Benign Keratosis, Vascular Lesion, etc.)  
- 📐 **Image Size**: Resized to 240x240 pixels  
- 📊 **Labels**: One-hot encoded  

---

## 🏗️ Project Structure

\`\`\`
📁 skin-disease-detection
├── README.md
├── model_training.ipynb        # Jupyter Notebook with training & evaluation
├── saved_models/
│   └── skin_disease_model_ISIC_densenet.h5
├── dataset/
│   ├── train/
│   └── val/
├── requirements.txt
\`\`\`

---

## 🔧 Models Implemented

| Model         | Pretrained | Params Frozen | Notes                         |
|---------------|------------|----------------|-------------------------------|
| CNN (custom)  | ❌          | N/A            | Built from scratch            |
| MobileNetV1   | ✅          | Most layers    | Lightweight and fast          |
| DenseNet121   | ✅          | Most layers    | Deep model with strong reuse  |

---

## 📈 Evaluation

Each model is trained for 5 epochs and evaluated on a validation split. Confusion matrices and accuracy/loss plots are generated.

---

## 🛠 Requirements

\`\`\`
certifi==2021.10.8  
click==8.0.3  
Flask==1.1.2  
gunicorn==20.1.0  
itsdangerous==2.0.1  
Jinja2==2.11.3  
MarkupSafe==1.1.1  
Werkzeug==2.0.2  
wincertstore==0.2  
pillow==8.4.0  
tensorflow==2.9.1  
\`\`\`

Install with:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

---

## 🚧 In Progress

- [ ] Add a simple Flask web app for real-time predictions  
- [ ] Improve CNN accuracy with data augmentation  
- [ ] Experiment with MobileNetV2 and EfficientNet  
- [ ] Add Grad-CAM for model explainability  

---

## 📷 Sample Results

> _Include accuracy/loss graphs and confusion matrix screenshots here_

---

## 🤝 Contributions

This project was created for academic purposes. Contributions are welcome as this project grows into a web-based diagnostic tool.

---
