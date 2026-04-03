import pandas as pd
import numpy as np
import json
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingClassifier

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from sklearn.pipeline import Pipeline


# ---------------- LOAD DATA ---------------- #

print("Loading selected features...")
# X_train = pd.read_csv("data/processed/X_train_selected.csv")
X_train = pd.read_csv("src/data/processed/X_train_imputed.csv")
y_train = pd.read_csv("src/data/processed/y_train_selected.csv")
# X_test = pd.read_csv("data/processed/X_test_selected.csv")
X_test = pd.read_csv("src/data/processed/X_test_imputed.csv")
y_test = pd.read_csv("src/data/processed/y_test_selected.csv")

y_train = y_train.values.ravel()
y_test = y_test.values.ravel()

# Encode labels for ROC-AUC & XGBoost
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

num_classes = len(np.unique(y_train_encoded))


# ---------------- DEFINE MODELS ---------------- #

models = {

    "LogisticRegression": Pipeline([
        # ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        ))
    ]),

     "RandomForest": Pipeline([
        # ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ]),

     "XGBoost": Pipeline([
        # ("imputer", SimpleImputer(strategy="median")),
        ("model", XGBClassifier(
            objective="multi:softprob",
            num_class=num_classes,
            eval_metric="mlogloss",
            random_state=42
        ))
    ]),

    # "NeuralNetwork": Pipeline([
    #     ("imputer", SimpleImputer(strategy="median")),
    #     ("scaler", StandardScaler()),
    #     ("model", MLPClassifier(
    #         hidden_layer_sizes=(64,),
    #         max_iter=200,
    #         early_stopping=True,
    #         random_state=42
    #     ))
    # ])
    "HistGradientBoosting": HistGradientBoostingClassifier(
    max_iter=200,
    random_state=42
)

}

# ---------------- TRAIN & EVALUATE ---------------- #

results = {}
best_accuracy = 0
best_model = None
best_model_name = None
best_y_pred=None

for name, model in models.items():

    print(f"\nTraining {name}...")

    if name == "XGBoost":
        model.fit(X_train, y_train_encoded)
        y_pred_encoded = model.predict(X_test)
        y_proba = model.predict_proba(X_test)
        y_pred = label_encoder.inverse_transform(y_pred_encoded)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)
        
    if name == "XGBoost":
        train_pred_encoded = model.predict(X_train)
        train_proba = model.predict_proba(X_train)
        train_pred = label_encoder.inverse_transform(train_pred_encoded)
    else:
        train_pred = model.predict(X_train)
        train_proba = model.predict_proba(X_train)


    # Metrics
    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted")
    rec = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")

    # ROC-AUC (multi-class)
    roc_auc = roc_auc_score(
        y_test_encoded,
        y_proba,
        multi_class="ovr",
        average="weighted"
    )

    print(f"{name} Train Accuracy: {train_acc:.4f}")
    print(f"{name} Test Accuracy: {test_acc:.4f}")
    print(f"{name} ROC-AUC: {roc_auc:.4f}")

    results[name] = {
        "Train Accuracy": float(train_acc),
        "Test Accuracy": float(test_acc),
        "Precision": float(prec),
        "Recall": float(rec),
        "F1 Score": float(f1),
        "ROC-AUC": float(roc_auc)
    }

    if test_acc > best_accuracy:
        best_accuracy = test_acc
        best_model = model
        best_model_name = name
        best_y_pred = y_pred


# ---------------- SAVE BEST MODEL ---------------- #

os.makedirs("models", exist_ok=True)
joblib.dump(best_model, "src/models/best_model.pkl")

# ---------------- CONFUSION MATRIX ---------------- #

cm = confusion_matrix(y_test, best_y_pred)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d",
            xticklabels=label_encoder.classes_,
            yticklabels=label_encoder.classes_)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title(f"Confusion Matrix - {best_model_name}")
plt.tight_layout()

os.makedirs("evaluation", exist_ok=True)
plt.savefig("evaluation/confusion_matrix.png")
plt.close()

print(f"\nBest Model: {best_model_name} ({best_accuracy:.4f})")
print("Confusion matrix saved.")

# ---------------- SAVE METRICS ---------------- #

with open("evaluation/metrics.json", "w") as f:
    json.dump(results, f, indent=4)

print("Metrics saved successfully.")


