from django.shortcuts import render
import os
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from lime.lime_tabular import LimeTabularExplainer

def home(request):
    return render(request, "Home.html")

def train_model():
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.ensemble import RandomForestClassifier, VotingClassifier
    from xgboost import XGBClassifier
    from catboost import CatBoostClassifier
    from sklearn.model_selection import train_test_split
    import numpy as np

    
    with open(r"predictor\Data.csv", "r") as f:
        lines = f.readlines()
    lines = [line.strip().replace('"', '') for line in lines]
    data = [line.split(',') for line in lines]

    df = pd.DataFrame(data[1:], columns=data[0])
    df.columns = df.columns.str.strip()

    
    df['Age'] = df['Age'].astype(float)
    df['Temperature'] = df['Temperature'].astype(float)

    
    X = df.drop("Disease", axis=1)
    y = df["Disease"]
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    
    numeric_features = ['Age', 'Temperature']
    categorical_features = ['Animal']
    binary_features = [col for col in X.columns if col not in numeric_features + categorical_features]

    
    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(sparse_output=False), categorical_features)
    ], remainder='passthrough')

    
    baseline_pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("rf", RandomForestClassifier(random_state=42))
    ])

    baseline_pipeline.fit(X, y_encoded)

    
    onehot_cols = baseline_pipeline.named_steps['preprocess'].named_transformers_['cat'].get_feature_names_out(categorical_features)
    all_features = numeric_features + list(onehot_cols) + binary_features

    importances = baseline_pipeline.named_steps['rf'].feature_importances_
    feat_imp = pd.Series(importances, index=all_features).sort_values(ascending=False)

    top_20_features = feat_imp.head(20).index.tolist()
    

    
    X_preprocessed = baseline_pipeline.named_steps['preprocess'].transform(X)
    X_pre_df = pd.DataFrame(X_preprocessed, columns=all_features)
    X_top20 = X_pre_df[top_20_features]
    X_top20_cleaned = X_top20.apply(pd.to_numeric, errors='coerce').fillna(0)

    
    X_train, X_test, y_train, y_test = train_test_split(X_top20_cleaned, y_encoded, test_size=0.2, random_state=42)

   
    xgb_model = XGBClassifier(
        objective='multi:softmax',
        num_class=len(set(y_encoded)),
        max_depth=6,
        learning_rate=0.1,
        n_estimators=100,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42
    )

    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )

    cat_model = CatBoostClassifier(
        iterations=200,
        depth=6,
        learning_rate=0.1,
        l2_leaf_reg=3,
        verbose=0,
        random_state=42
    )

    
    voting_clf = VotingClassifier(
        estimators=[('rf', rf_model), ('xgb', xgb_model), ('cat', cat_model)],
        voting='soft'
    )

    voting_clf.fit(X_train, y_train)
    disease_target_names = le.classes_
    return voting_clf,disease_target_names,baseline_pipeline, top_20_features

rf_model,dtn,preprocess_pipe, top_20 = train_model()


SYMPTOMS = [
    'Temperature', 'painless lumps', 'Age', 'blisters on hooves', 'blisters on tongue',
    'blisters on gums', 'swelling in limb', 'swelling in muscle', 'blisters on mouth',
    'crackling sound', 'lameness', 'swelling in abdomen', 'swelling in neck',
    'chest discomfort', 'fever', 'shortness of breath', 'swelling in extremities',
    'difficulty walking', 'chills', 'depression'
]

from .forms import SymptomForm

def predict_disease(symptom_dict):
    import pandas as pd

    # Step 1: Build full input DataFrame with all SYMPTOMS
    input_row = {feature: 0 for feature in SYMPTOMS}
    input_row['Age'] = symptom_dict.get('Age', 5)
    input_row['Temperature'] = symptom_dict.get('Temperature', 37)
    for symptom in SYMPTOMS:
        if symptom not in ['Age', 'Temperature']:
            input_row[symptom] = symptom_dict.get(symptom, 0)
    input_df = pd.DataFrame([input_row])

    # Step 2: Preprocess only numeric + binary (skip 'Animal' since it wasn't selected)
    numeric_features = ['Age', 'Temperature']
    binary_features = [col for col in SYMPTOMS if col not in numeric_features]

    X_top_input = input_df[numeric_features + binary_features]

    # Step 3: Scale numeric features (match training logic)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaler.fit(input_df[numeric_features])  # dummy fit, for consistency

    X_top_input[numeric_features] = scaler.transform(X_top_input[numeric_features])

    # Step 4: Select only the top 20 features (already known from train_model)
    X_final = X_top_input[top_20].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Step 5: Predict
    prediction = rf_model.predict(X_final)
    return dtn[prediction[0]]



def symptom_check(request):
    if request.method == 'POST':
        form = SymptomForm(request.POST)
        if form.is_valid():
            symptoms_selected = form.cleaned_data['symptoms']
            symptom_dict = {symptom: 0 for symptom in SYMPTOMS}

            for symptom in symptoms_selected:
                symptom_dict[symptom] = 1

            # Extract Age and Temperature from input fields
            try:
                age = float(request.POST.get('age', 5))
            except (TypeError, ValueError):
                age = 5  # Fallback default

            try:
                temperature = float(request.POST.get('temperature', 37))
            except (TypeError, ValueError):
                temperature = 37  # Fallback default

            symptom_dict['Age'] = age
            symptom_dict['Temperature'] = temperature

            predicted_disease = predict_disease(symptom_dict)

            print("Selected Symptoms from form:", symptoms_selected)
            print("Symptom dict going to prediction:", symptom_dict)

            return render(request, 'result.html', {'disease': predicted_disease})
    else:
        form = SymptomForm()
    return render(request, 'form.html', {'form': form})

