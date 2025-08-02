# 🐄 Livestock Disease Prediction System

A Machine Learning-powered web application to predict diseases in livestock based on symptoms and external features such as temperature and age. Built using Django (backend), HTML/CSS (frontend), and ensemble models like XGBoost, Random Forest, and CatBoost for accurate disease classification.

---

## 🚀 Features

- Predict livestock diseases using clinical signs and environmental data
- Ensemble ML model combining XGBoost, Random Forest, and CatBoost
- Clean and responsive HTML/CSS frontend
- Built with Django framework for scalable backend logic

---

## 🧠 Machine Learning Models

The backend uses a voting ensemble of the following models trained on a labeled dataset:

- **XGBoost**
- **Random Forest**
- **CatBoost**

### 📊 Input Features

- `Temperature`
- `painless lumps`
- `Age`
- `blisters on hooves`
- `blisters on tongue`
- `blisters on gums`
- `swelling in limb`
- `swelling in muscle`
- `blisters on mouth`
- `crackling sound`
- `lameness`
- `swelling in abdomen`
- `swelling in neck`
- `chest discomfort`
- `fever`
- `shortness of breath`
- `swelling in extremities`
- `difficulty walking`
- `chills`
- `depression`

---

## 🛠 Tech Stack

| Layer      | Technology       |
|------------|------------------|
| Backend    | Django (Python)  |
| Frontend   | HTML, CSS        |
| ML Models  | XGBoost, Random Forest, CatBoost |
| Deployment | (Optional) Heroku / Azure / Render |

---

## 🖼️ UI Overview

- Homepage: Symptom selection using checkboxes
- Form: Users enter values for all symptoms and temperature/age
- Output: Predicted disease label with probability score

---

## ⚙️ How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/livestock-disease-predictor.git
   cd livestock-disease-predictor
