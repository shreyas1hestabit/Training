# import pandas as pd
# import json
# import joblib
# from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
# from sklearn.preprocessing import StandardScaler
# from sklearn.impute import SimpleImputer
# from sklearn.pipeline import Pipeline
# from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
# from xgboost import XGBClassifier
# from sklearn.neural_network import MLPClassifier


# # Load train data
# print("Loading selected features...")

# X_train = pd.read_csv("data/processed/X_train_selected.csv")
# y_train = pd.read_csv("data/processed/y_train_selected.csv")
# X_test = pd.read_csv("data/processed/X_test_selected.csv")
# y_test = pd.read_csv("data/processed/y_test_selected.csv")
# assert list(X_train.columns)== list(X_test.columns)
# print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
# print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

# y_train = y_train.values.ravel()
# y_test = y_test.values.ravel()

# # Define 4 models
# models = {
#     "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
#     "RandomForest": RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42),
#     "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="mlogloss", random_state=42),
#     "NeuralNetwork": MLPClassifier(hidden_layer_sizes=(64,32), max_iter=300, random_state=42)
# }

# def create_pipeline(model):
#     # Impute missing numeric values with 0 and scale
#     pipeline = Pipeline([
#         ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
#         ("scaler", StandardScaler()),
#         ("model", model)
#     ])
#     return pipeline


# best_model = None
# best_score = 0
# metrics_dict = {}

# for name, model in models.items():
#     print(f"\nTraining {name}...")
    
#     pipeline = create_pipeline(model)
#     pipeline.fit(X_train, y_train)
    
#     # Predict on test set
#     y_pred = pipeline.predict(X_test)


# # Train models on training data
# # for name, model in models.items():
# #     print(f"Training {name}...")
# #     model.fit(X_train, y_train.values.ravel())  # train
# #     print(f"{name} training completed!\n")


# training/train.py
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

# ---------------- LOAD DATA ---------------- #
print("Loading selected features...")
X_train = pd.read_csv("data/processed/X_train_selected.csv")
y_train = pd.read_csv("data/processed/y_train_selected.csv")
X_test = pd.read_csv("data/processed/X_test_selected.csv")
y_test = pd.read_csv("data/processed/y_test_selected.csv")

print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

# ---------------- HANDLE MISSING VALUES ---------------- #
print("\nImputing missing values...")
imputer = SimpleImputer(strategy="median")
X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
X_test = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)

# ---------------- ENCODE LABELS FOR XGBOOST ---------------- #
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train.values.ravel())
y_test_encoded = label_encoder.transform(y_test.values.ravel())

# ---------------- DEFINE MODELS ---------------- #
models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="mlogloss", random_state=42),
    "NeuralNetwork": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, random_state=42)
}

# ---------------- TRAIN AND EVALUATE ---------------- #
results = {}
best_model_name = None
best_accuracy = 0
best_model_instance = None

for name, model in models.items():
    print(f"\nTraining {name}...")

    # For XGBoost, use encoded labels
    if name == "XGBoost":
        model.fit(X_train, y_train_encoded)
        y_pred = model.predict(X_test)
        y_pred_labels = label_encoder.inverse_transform(y_pred)
        y_true_labels = y_test.values.ravel()
    else:
        model.fit(X_train, y_train.values.ravel())
        y_pred_labels = model.predict(X_test)
        y_true_labels = y_test.values.ravel()

    # Metrics
    acc = accuracy_score(y_true_labels, y_pred_labels)
    prec = precision_score(y_true_labels, y_pred_labels, average="weighted")
    rec = recall_score(y_true_labels, y_pred_labels, average="weighted")
    f1 = f1_score(y_true_labels, y_pred_labels, average="weighted")

    # Store results
    results[name] = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1 Score": f1
    }

    print(f"{name} Accuracy: {acc:.4f}, F1 Score: {f1:.4f}")

    # Track best model
    if acc > best_accuracy:
        best_accuracy = acc
        best_model_name = name
        best_model_instance = model

# ---------------- SAVE BEST MODEL ---------------- #
os.makedirs("models", exist_ok=True)
best_model_path = "models/best_model.pkl"
import joblib
joblib.dump(best_model_instance, best_model_path)
print(f"\nBest model: {best_model_name} saved at {best_model_path}")

# ---------------- SAVE METRICS ---------------- #
os.makedirs("evaluation", exist_ok=True)
metrics_path = "evaluation/metrics.json"
with open(metrics_path, "w") as f:
    json.dump(results, f, indent=4)
print(f"Metrics saved at {metrics_path}")

# ---------------- PLOT CONFUSION MATRIX FOR BEST MODEL ---------------- #


