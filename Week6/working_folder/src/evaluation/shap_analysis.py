# # import os
# # import joblib
# # import pandas as pd
# # import numpy as np
# # import shap
# # import matplotlib.pyplot as plt
# # from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
# # from sklearn.preprocessing import LabelEncoder

# # # ---------------- PATHS ---------------- #

# # BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # src/
# # MODEL_PATH = os.path.join(BASE_DIR, "models", "tuned_model.pkl")
# # EVAL_DIR = os.path.join(BASE_DIR, "evaluation", "shap_plots")
# # os.makedirs(EVAL_DIR, exist_ok=True)

# # X_train_path = os.path.join(BASE_DIR, "data/processed/X_train_selected.csv")
# # y_train_path = os.path.join(BASE_DIR, "data/processed/y_train_selected.csv")
# # X_test_path = os.path.join(BASE_DIR, "data/processed/X_test_selected.csv")
# # y_test_path = os.path.join(BASE_DIR, "data/processed/y_test_selected.csv")

# # # ---------------- LOAD DATA ---------------- #

# # X_train = pd.read_csv(X_train_path)
# # y_train = pd.read_csv(y_train_path).values.ravel()
# # X_test = pd.read_csv(X_test_path)
# # y_test = pd.read_csv(y_test_path).values.ravel()

# # # Encode labels
# # label_encoder = LabelEncoder()
# # y_train_encoded = label_encoder.fit_transform(y_train)
# # y_test_encoded = label_encoder.transform(y_test)

# # # ---------------- LOAD MODEL ---------------- #

# # best_model = joblib.load(MODEL_PATH)

# # # ---------------- SHAP EXPLAINER ---------------- #

# # print("Generating SHAP values...")
# # # explainer = shap.Explainer(best_model.predict,X_test)
# # # shap_values = explainer(X_test)
# # explainer=shap.TreeExplainer(best_model)
# # shap_values=explainer.shap_values(X_test)

# # # SHAP summary plot (bar)
# # plt.figure(figsize=(10,6))
# # shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
# # plt.tight_layout()
# # bar_plot_file = os.path.join(EVAL_DIR, "shap_summary_bar.png")
# # plt.savefig(bar_plot_file)
# # plt.close()
# # print(f"Saved SHAP summary bar plot: {bar_plot_file}")

# # # SHAP summary plot (beeswarm)
# # plt.figure(figsize=(10,6))
# # shap.summary_plot(shap_values, X_test, show=False)
# # plt.tight_layout()
# # beeswarm_file = os.path.join(EVAL_DIR, "shap_summary_beeswarm.png")
# # plt.savefig(beeswarm_file)
# # plt.close()
# # print(f"Saved SHAP beeswarm plot: {beeswarm_file}")

# # # ---------------- FEATURE IMPORTANCE ---------------- #

# # # feature_importances = best_model.feature_importances_
# # # features = X_train.columns

# # # plt.figure(figsize=(10,6))
# # # plt.barh(features, feature_importances)
# # # plt.xlabel("Importance")
# # # plt.title("Feature Importance (HGB)")
# # # plt.tight_layout()
# # # fi_file = os.path.join(LOG_DIR, "feature_importance.png")
# # # plt.savefig(fi_file)
# # # plt.close()
# # # print(f"Saved feature importance chart: {fi_file}")

# # # SHAP-based feature importance
# # shap_importance = np.abs(shap_values).mean(axis=0)  # average absolute SHAP values per feature
# # features = X_train.columns

# # plt.figure(figsize=(10,6))
# # plt.barh(features, shap_importance)
# # plt.xlabel("Mean |SHAP value|")
# # plt.title("Feature Importance (SHAP)")
# # plt.tight_layout()
# # fi_file = os.path.join(EVAL_DIR, "feature_importance.png")
# # plt.savefig(fi_file)
# # plt.close()
# # print(f"Saved SHAP-based feature importance chart: {fi_file}")

# # # ---------------- CONFUSION MATRIX ---------------- #

# # preds = best_model.predict(X_test)
# # cm = confusion_matrix(y_test, preds, labels=label_encoder.classes_)
# # disp = ConfusionMatrixDisplay(cm, display_labels=label_encoder.classes_)
# # disp.plot(cmap="Blues", xticks_rotation=45)
# # plt.title("Confusion Matrix")
# # cm_file = os.path.join(EVAL_DIR, "confusion_matrix_shap.png")
# # plt.tight_layout()
# # plt.savefig(cm_file)
# # plt.close()
# # print(f"Saved confusion matrix: {cm_file}")

# # print("\nSHAP analysis completed successfully.")


# import os
# import joblib
# import pandas as pd
# import numpy as np
# import shap
# import matplotlib.pyplot as plt
# from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
# from sklearn.preprocessing import LabelEncoder

# # ---------------- PATHS ---------------- #
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # src/
# MODEL_PATH = os.path.join(BASE_DIR, "models", "tuned_model.pkl")
# EVAL_DIR = os.path.join(BASE_DIR, "evaluation", "shap_plots")
# os.makedirs(EVAL_DIR, exist_ok=True)

# X_train_path = os.path.join(BASE_DIR, "data/processed/X_train_selected.csv")
# y_train_path = os.path.join(BASE_DIR, "data/processed/y_train_selected.csv")
# X_test_path = os.path.join(BASE_DIR, "data/processed/X_test_selected.csv")
# y_test_path = os.path.join(BASE_DIR, "data/processed/y_test_selected.csv")

# # ---------------- LOAD DATA ---------------- #
# print("Loading data...")
# X_train = pd.read_csv(X_train_path)
# y_train = pd.read_csv(y_train_path).values.ravel()
# X_test = pd.read_csv(X_test_path)
# y_test = pd.read_csv(y_test_path).values.ravel()

# # Encode labels
# label_encoder = LabelEncoder()
# y_train_encoded = label_encoder.fit_transform(y_train)
# y_test_encoded = label_encoder.transform(y_test)

# # ---------------- LOAD MODEL ---------------- #
# print("Loading trained model...")
# best_model = joblib.load(MODEL_PATH)

# # ---------------- SHAP EXPLAINER ---------------- #
# print("Generating SHAP values...")
# explainer = shap.TreeExplainer(best_model)
# shap_values_full = explainer.shap_values(X_test)  # Multi-class: list of arrays

# # ---------------- SHAP SUMMARY PLOTS ---------------- #
# # Bar plot
# plt.figure(figsize=(10,6))
# # if isinstance(shap_values, list):
# #     # Multi-class: average over classes
# #     shap_abs = np.array([np.abs(s).mean(axis=0) for s in shap_values])  # (num_classes, num_features)
# #     shap_importance = shap_abs.mean(axis=0)  # average across classes -> 1D
# # else:
# #     shap_importance = np.abs(shap_values).mean(axis=0)

# if isinstance(shap_values_full, list):
#     shap_values_mean = np.mean([np.abs(s).mean(axis=0) for s in shap_values_full], axis=0)
# else:
#     shap_values_mean = np.abs(shap_values_full).mean(axis=0)

# # shap.summary_plot(shap_importance, X_test, plot_type="bar", show=False)
# # plt.tight_layout()
# # bar_file = os.path.join(EVAL_DIR, "shap_summary_bar.png")
# # plt.savefig(bar_file)
# # plt.close()
# # print(f"Saved SHAP summary bar plot: {bar_file}")
# # plt.figure(figsize=(10,6))
# plt.barh(X_test.columns, shap_values_mean)
# plt.xlabel("Mean |SHAP value|")
# plt.title("Feature Importance (SHAP, averaged across classes)")
# plt.tight_layout()
# bar_file = os.path.join(EVAL_DIR, "shap_summary_bar.png")
# plt.savefig(os.path.join(bar_file))
# plt.close()
# print(f"Saved SHAP summary bar plot: {bar_file}")

# # Beeswarm plot
# # plt.figure(figsize=(10,6))
# # shap.summary_plot(shap_values, X_test, show=False)  # Use raw shap_values
# # plt.tight_layout()
# # beeswarm_file = os.path.join(EVAL_DIR, "shap_summary_beeswarm.png")
# # plt.savefig(beeswarm_file)
# # plt.close()
# plt.figure(figsize=(10,6))
# shap.summary_plot(shap_values_full, X_test, show=False)
# beeswarm_file = os.path.join(EVAL_DIR, "shap_summary_beeswarm.png")
# plt.savefig(os.path.join(beeswarm_file))
# plt.close()
# print(f"Saved SHAP summary beeswarm plot: {beeswarm_file}")

# # ---------------- FEATURE IMPORTANCE (HGB) ---------------- #
# features = X_train.columns
# if hasattr(best_model, "feature_importances_"):
#     fi = best_model.feature_importances_
#     plt.figure(figsize=(10,6))
#     plt.barh(features, fi)
#     plt.xlabel("Importance")
#     plt.title("Feature Importance (HGB Model)")
#     plt.tight_layout()
#     fi_file = os.path.join(EVAL_DIR, "feature_importance_hgb.png")
#     plt.savefig(fi_file)
#     plt.close()
#     print(f"Saved HGB feature importance chart: {fi_file}")
# else:
#     print("Warning: Model does not have feature_importances_ attribute.")

# # ---------------- FEATURE IMPORTANCE (SHAP) ---------------- #
# plt.figure(figsize=(10,6))
# plt.barh(features, shap_values_mean)
# plt.xlabel("Importance")
# plt.title("Feature Importance (SHAP, averaged across classes)")
# plt.tight_layout()
# shap_fi_file = os.path.join(EVAL_DIR, "feature_importance_shap.png")
# plt.savefig(shap_fi_file)
# plt.close()
# print(f"Saved SHAP-based feature importance chart: {shap_fi_file}")

# # ---------------- CONFUSION MATRIX ---------------- #
# preds = best_model.predict(X_test)
# cm = confusion_matrix(y_test, preds, labels=label_encoder.classes_)
# disp = ConfusionMatrixDisplay(cm, display_labels=label_encoder.classes_)
# disp.plot(cmap="Blues", xticks_rotation=45)
# plt.title("Confusion Matrix")
# plt.tight_layout()
# cm_file = os.path.join(EVAL_DIR, "confusion_matrix.png")
# plt.savefig(cm_file)
# plt.close()
# print(f"Saved confusion matrix: {cm_file}")

# print("\nSHAP analysis completed successfully.")


import os
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import LabelEncoder

# ---------------- PATHS ---------------- #
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "tuned_model.pkl")
EVAL_DIR = os.path.join(BASE_DIR, "evaluation", "shap_plots")
os.makedirs(EVAL_DIR, exist_ok=True)

X_train_path = os.path.join(BASE_DIR, "data/processed/X_train_selected.csv")
y_train_path = os.path.join(BASE_DIR, "data/processed/y_train_selected.csv")
X_test_path  = os.path.join(BASE_DIR, "data/processed/X_test_selected.csv")
y_test_path  = os.path.join(BASE_DIR, "data/processed/y_test_selected.csv")

# ---------------- LOAD DATA ---------------- #
print("Loading data...")
X_train = pd.read_csv(X_train_path)
y_train = pd.read_csv(y_train_path).values.ravel()
X_test  = pd.read_csv(X_test_path)
y_test  = pd.read_csv(y_test_path).values.ravel()

# ---------------- ENCODE LABELS ---------------- #
label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded  = label_encoder.transform(y_test)
print(f"Classes: {label_encoder.classes_}")

# ---------------- LOAD MODEL ---------------- #
print("Loading trained model...")
best_model = joblib.load(MODEL_PATH)
print(f"Model type: {type(best_model).__name__}")

# ---------------- SAMPLE FOR SHAP (HGB is slow) ---------------- #
# HGB SHAP is computed via sampling - keep small to avoid memory issues
X_test_sample = X_test.sample(n=min(300, len(X_test)), random_state=42)
X_train_sample = X_train.sample(n=min(100, len(X_train)), random_state=42)

print(f"Using {len(X_test_sample)} test samples for SHAP...")

# ---------------- SHAP EXPLAINER FOR HGB ---------------- #
# TreeExplainer does NOT work well with sklearn HGB
# Use shap.Explainer which auto-selects the right method
# masker handles the background distribution
print("Building SHAP explainer..")

masker = shap.maskers.Independent(X_train_sample)
explainer = shap.Explainer(best_model.predict_proba, masker)

print("Computing SHAP values...")
shap_values_obj = explainer(X_test_sample)

# shap_values_obj.values shape: (n_samples, n_features, n_classes)
shap_values = shap_values_obj.values
print(f"SHAP values shape: {shap_values.shape}")

# Average absolute SHAP across all samples and all classes -> (n_features,)
shap_values_mean = np.abs(shap_values).mean(axis=(0, 2))
feat_names = X_test_sample.columns.tolist()
sorted_idx = np.argsort(shap_values_mean)

print("SHAP values computed successfully!")

# ---------------- PLOT 1: SHAP BAR SUMMARY ---------------- #
print("Saving SHAP bar summary plot...")
plt.figure(figsize=(10, 8))
plt.barh(
    [feat_names[i] for i in sorted_idx],
    shap_values_mean[sorted_idx],
    color="steelblue"
)
plt.xlabel("Mean |SHAP value|")
plt.title("Feature Importance (SHAP - averaged across all classes)")
plt.tight_layout()
bar_file = os.path.join(EVAL_DIR, "shap_summary_bar.png")
plt.savefig(bar_file, dpi=150)
plt.close()
print(f"Saved: {bar_file}")

# ---------------- PLOT 2: BEESWARM (per class) ---------------- #
print("Saving SHAP beeswarm plots (one per class)...")
for i, class_name in enumerate(label_encoder.classes_):
    plt.figure(figsize=(10, 6))

    # shap_values[:, :, i] -> (n_samples, n_features) for class i
    shap.summary_plot(
        shap_values[:, :, i],
        X_test_sample,
        feature_names=feat_names,
        show=False,
        plot_type="dot"
    )
    plt.title(f"SHAP Beeswarm - Class: {class_name}")
    plt.tight_layout()
    beeswarm_file = os.path.join(EVAL_DIR, f"shap_beeswarm_{class_name}.png")
    plt.savefig(beeswarm_file, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"  Saved: {beeswarm_file}")

# ---------------- PLOT 3: MODEL FEATURE IMPORTANCE ---------------- #
if hasattr(best_model, "feature_importances_"):
    print("Saving model feature importance plot...")
    fi = best_model.feature_importances_
    sorted_fi_idx = np.argsort(fi)

    plt.figure(figsize=(10, 8))
    plt.barh(
        [feat_names[i] for i in sorted_fi_idx],
        fi[sorted_fi_idx],
        color="coral"
    )
    plt.xlabel("Importance")
    plt.title("Feature Importance (HistGradientBoosting)")
    plt.tight_layout()
    fi_file = os.path.join(EVAL_DIR, "feature_importance_hgb.png")
    plt.savefig(fi_file, dpi=150)
    plt.close()
    print(f"Saved: {fi_file}")
else:
    print("Note: HGB does not expose feature_importances_ ")

# ---------------- PLOT 4: SHAP FEATURE IMPORTANCE (sorted) ---------------- #
print("Saving SHAP-based feature importance plot...")
plt.figure(figsize=(10, 8))
plt.barh(
    [feat_names[i] for i in sorted_idx],
    shap_values_mean[sorted_idx],
    color="mediumseagreen"
)
plt.xlabel("Mean |SHAP value|")
plt.title("Feature Importance (SHAP)")
plt.tight_layout()
shap_fi_file = os.path.join(EVAL_DIR, "feature_importance_shap.png")
plt.savefig(shap_fi_file, dpi=150)
plt.close()
print(f"Saved: {shap_fi_file}")

# ---------------- PLOT 5: CONFUSION MATRIX ---------------- #
print("Saving confusion matrix...")

# HGB predict() directly returns class labels (not encoded integers)
# so NO inverse_transform needed
preds = best_model.predict(X_test)

cm = confusion_matrix(y_test, preds, labels=label_encoder.classes_)
disp = ConfusionMatrixDisplay(cm, display_labels=label_encoder.classes_)

fig, ax = plt.subplots(figsize=(8, 6))
disp.plot(cmap="Blues", xticks_rotation=45, ax=ax)
plt.title("Confusion Matrix - HistGradientBoosting")
plt.tight_layout()
cm_file = os.path.join(EVAL_DIR, "confusion_matrix.png")
plt.savefig(cm_file, dpi=150)
plt.close()
print(f"Saved: {cm_file}")

print("\n SHAP analysis completed successfully.")
