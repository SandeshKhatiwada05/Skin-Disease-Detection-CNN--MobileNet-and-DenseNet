<h1>AI for Skin Disease Detection</h1>

A multi-class skin disease classifier using CNN, DenseNet121, and MobileNetV1 on the DermNet dataset.

---

## Project Overview

This project applies deep learning to dermatology by classifying 23 types of common skin diseases using image data. It compares performance across a custom CNN, MobileNetV1, and DenseNet121 using TensorFlow and Keras.

---

## Current Features

- Data preprocessing from the DermNet dataset  
- Custom CNN model implemented from scratch  
- Transfer learning with MobileNetV1  
- Transfer learning with DenseNet121  
- Training, validation, and testing splits  
- Accuracy & loss visualization using Seaborn  
- Confusion matrix evaluation using Scikit-plot  

---

## Dataset

- **Source**: https://www.kaggle.com/datasets/riyaelizashaju/skin-disease-classification-image-dataset  
- **Classes**: 9 skin conditions 
- **Image Size**: Resized to 240x240 pixels  
- **Labels**: One-hot encoded  


---

## 🔧 Models Implemented

| Model         | Pretrained | Params Frozen | Notes                         |
|---------------|------------|----------------|-------------------------------|
| CNN (custom)  | ❌          | N/A            | Built from scratch            |
| MobileNetV1   | ✅          | Most layers    | Lightweight and fast          |
| DenseNet121   | ✅          | Most layers    | Deep model with strong reuse  |

---

## Evaluation

Each model is trained for 5 epochs and evaluated on a validation split. Confusion matrices and accuracy/loss plots are generated.

---

## Requirements

```
use conda to install the environment_full.yml
```

---

## Sample Results
<img width="613" height="488" alt="image" src="https://github.com/user-attachments/assets/08da86c6-68b3-42d8-b144-0e11882814b2" />
<img width="575" height="647" alt="image" src="https://github.com/user-attachments/assets/4454d1c0-0bef-40eb-94cf-86d5f596bfc0" />
<img width="865" height="637" alt="image" src="https://github.com/user-attachments/assets/899e176d-009e-4083-bf29-a3ea547e15d1" />
<img width="865" height="744" alt="image" src="https://github.com/user-attachments/assets/95b3f2e3-cfc6-4075-944a-82b14d56ffba" />


---

## Contributions

This project was created for academic purposes. Contributions are welcome as this project grows into a web-based diagnostic tool.
All the documentations and resources will be uploaded after after completion of the project.

---

Larger database containing project will be available very soon
