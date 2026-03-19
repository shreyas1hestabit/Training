# import pandas as pd
# import numpy as np
# import optuna
# import json
# import os
# import joblib

# from sklearn.ensemble import HistGradientBoostingClassifier
# from sklearn.metrics import accuracy_score, roc_auc_score
# # from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# # from sklearn.impute import SimpleImputer
# # from sklearn.pipeline import Pipeline

# import logging

# # Path to the logs folder in src/logs/
# LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "tuning")
# os.makedirs(LOG_DIR, exist_ok=True)
# LOG_FILE = os.path.join(LOG_DIR, "tuning.log")

# import logging
# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )



# # ---------------- LOAD DATA ---------------- #

# logging.info("Loading selected features...")

# # X_train = pd.read_csv("data/processed/X_train_selected.csv")
# X_train = pd.read_csv("src/data/processed/X_train_imputed.csv")
# y_train = pd.read_csv("src/data/processed/y_train_selected.csv")
# # X_test = pd.read_csv("src/data/processed/X_test_selected.csv")
# X_test = pd.read_csv("src/data/processed/X_test_imputed.csv")
# y_test = pd.read_csv("src/data/processed/y_test_selected.csv")

# y_train = y_train.values.ravel()
# y_test = y_test.values.ravel()

# # Encode labels
# label_encoder = LabelEncoder()
# y_train_encoded = label_encoder.fit_transform(y_train)
# y_test_encoded = label_encoder.transform(y_test)

# num_classes = len(np.unique(y_train_encoded))


# # ---------------- BASELINE MODEL ---------------- #

# baseline_model = HistGradientBoostingClassifier(
#     random_state=42
# )

# baseline_model.fit(X_train, y_train)
# baseline_pred = baseline_model.predict(X_test)
# baseline_acc = accuracy_score(y_test, baseline_pred)

# print(f"\nBaseline Accuracy: {baseline_acc:.4f}")
# logging.info(f"baseline accuracy: {baseline_acc:.4f}")


# # ---------------- OPTUNA OBJECTIVE ---------------- #

# def objective(trial):

#     params = {
#         # "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
#         # "max_iter": trial.suggest_int("max_iter", 100, 400),
#         # "max_depth": trial.suggest_int("max_depth", 3, 15),
#         # "max_leaf_nodes": trial.suggest_int("max_leaf_nodes", 15, 100),
#         # "random_state": 42
#         "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
#         "max_iter": trial.suggest_int("max_iter", 200, 600),
#         "max_depth": trial.suggest_int("max_depth", 3, 20),
#         "max_leaf_nodes": trial.suggest_int("max_leaf_nodes", 15, 128),
#         "min_samples_leaf": trial.suggest_int("min_samples_leaf", 20, 100),
#         "max_bins": trial.suggest_int("max_bins", 128, 255),
#         "l2_regularization": trial.suggest_float("l2_regularization", 0.0, 1.0),
#         "random_state": 42
#     }

#     model = HistGradientBoostingClassifier(**params)

#     model.fit(X_train, y_train)

#     preds = model.predict(X_test)
#     acc = accuracy_score(y_test, preds)

#     return acc


# # ---------------- RUN OPTUNA ---------------- #

# study = optuna.create_study(direction="maximize")
# study.optimize(objective, n_trials=40)

# print("\nBest Trial:")
# print(study.best_trial.params)
# print(f"Best Accuracy: {study.best_value:.4f}")

# logging.info(f"Best Trial Parameters: {study.best_trial.params}")
# logging.info(f"Best Trial Accuracy: {study.best_value:.4f}")


# # ---------------- TRAIN BEST MODEL ---------------- #

# best_params = study.best_trial.params

# best_model = HistGradientBoostingClassifier(
#     **best_params,
#     random_state=42
# )

# best_model.fit(X_train, y_train)

# best_preds = best_model.predict(X_test)
# best_acc = accuracy_score(y_test, best_preds)

# print(f"\nTuned Accuracy: {best_acc:.4f}")
# logging.info(f"Tuned Accuracy: {best_acc:.4f}")

# # ---------------- SAVE RESULTS ---------------- #

# os.makedirs("tuning", exist_ok=True)

# results = {
#     "Baseline Accuracy": float(baseline_acc),
#     "Tuned Accuracy": float(best_acc),
#     "Best Parameters": best_params
# }

# with open("tuning/results.json", "w") as f:
#     json.dump(results, f, indent=4)

# # Save tuned model
# os.makedirs("models", exist_ok=True)
# joblib.dump(best_model, "models/tuned_model.pkl")

# logging.info("tunning completed")
# print("\nTuning completed successfully.")

import pandas as pd
import numpy as np
import optuna
import json
import os
import joblib
import logging
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
# ---------------- PATH CONFIGURATION ---------------- #
# Root directory (Week6) se paths define kar rahe hain
BASE_DIR = "src"
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "models")
TUNING_DIR = os.path.join(BASE_DIR, "tuning")
LOG_DIR = os.path.join(BASE_DIR, "logs", "tuning")

# Folders create karein agar nahi hain
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(TUNING_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "tuning.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------- LOAD DATA ---------------- #
logging.info("Loading selected features...")

# Paths updated to src/data/processed/...
X_train = pd.read_csv(os.path.join(DATA_DIR, "X_train_imputed.csv"))
y_train = pd.read_csv(os.path.join(DATA_DIR, "y_train_selected.csv"))
X_test = pd.read_csv(os.path.join(DATA_DIR, "X_test_imputed.csv"))
y_test = pd.read_csv(os.path.join(DATA_DIR, "y_test_selected.csv"))

y_train = y_train.values.ravel()
y_test = y_test.values.ravel()

label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

# ---------------- BASELINE MODEL ---------------- #
baseline_model = HistGradientBoostingClassifier(random_state=42)
baseline_model.fit(X_train, y_train)
baseline_pred = baseline_model.predict(X_test)
baseline_acc = accuracy_score(y_test, baseline_pred)

print(f"\nBaseline Accuracy: {baseline_acc:.4f}")
logging.info(f"Baseline accuracy: {baseline_acc:.4f}")

# ---------------- OPTUNA OBJECTIVE ---------------- #
def objective(trial):
    # XGBoost specific hyperparameter space
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 200, 1000), #total no of trees built. optuna ki range is 200 to 1000
        "max_depth": trial.suggest_int("max_depth", 3, 10), #how deep each tree can go. min 3 max 10
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True), #learning rate is the step i.e. how fast the model learns.
        #log=true tells optuna to search more carefully at smaller values.
        "subsample": trial.suggest_float("subsample", 0.5, 1.0), #percentage of rows used for each tree
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0), #percentage of columns used for each tree
        "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True), #min loss required to make a further split on leaf node 
        #It acts as a Regularization parameter. It tells the tree: "Don't split this branch unless it significantly improves the prediction." This makes the model more conservative and less likely to overfit.
        "random_state": 42,
        "tree_method": "hist", # Fast histogram-based method This is an architectural optimization. Instead of looking at every single data point to find a split, XGBoost groups the values into "bins" (like a histogram). This makes training much faster on large datasets.
        "device": "cpu"        # Or "cuda" if you have a GPU
    }
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train_encoded)
    preds = model.predict(X_test)
    return accuracy_score(y_test_encoded, preds)

# ---------------- RUN OPTUNA ---------------- #
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=40)

print(f"\nBest Accuracy: {study.best_value:.4f}")
logging.info(f"Best Trial Accuracy: {study.best_value:.4f}")

# ---------------- TRAIN & SAVE BEST MODEL ---------------- #
best_params = study.best_trial.params
best_model = HistGradientBoostingClassifier(**best_params, random_state=42)
best_model.fit(X_train, y_train)

tuned_acc = accuracy_score(y_test, best_model.predict(X_test))
print(f"Tuned Accuracy: {tuned_acc:.4f}")

# Save results to src/tuning/results.json
results = {
    "Baseline Accuracy": float(baseline_acc),
    "Tuned Accuracy": float(tuned_acc),
    "Best Parameters": best_params
}
with open(os.path.join(TUNING_DIR, "results.json"), "w") as f:
    json.dump(results, f, indent=4)

# Save tuned model to src/models/tuned_model.pkl
joblib.dump(best_model, os.path.join(MODEL_DIR, "tuned_model.pkl"))

logging.info("Tuning completed successfully.")
print("\nTuning completed. Model saved in src/models/tuned_model.pkl")
