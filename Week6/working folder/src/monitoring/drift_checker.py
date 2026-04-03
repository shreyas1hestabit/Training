import pandas as pd
import numpy as np
import json
import os

# ---------------- CONFIG ---------------- #

TRAIN_PATH = "src/data/processed/X_train_selected.csv"
LOG_PATH = "src/prediction_logs.csv"
OUTPUT_PATH = "src/monitoring/drift_report.json"

DRIFT_THRESHOLD = 0.2  # 20% mean shift allowed


# ---------------- LOAD DATA ---------------- #

def load_data():
    if not os.path.exists(TRAIN_PATH):
        raise FileNotFoundError("Training data not found at {TRAIN_PATH}")

    if not os.path.exists(LOG_PATH):
        raise FileNotFoundError("Prediction logs not found at {LOG_PATH}")
        return None, None

    train_df = pd.read_csv(TRAIN_PATH)
    log_df = pd.read_csv(LOG_PATH)

    return train_df, log_df


# ---------------- DRIFT CHECK ---------------- #

def calculate_drift(train_df, log_df):

    # Remove non-feature columns from logs
    # log_df = log_df.drop(columns=["prediction", "request_id", "timestamp"], errors="ignore")

    # drift_results = {}

    drift_results = {}
    
    # Identify numeric columns that exist in BOTH dataframes
    # This prevents trying to calculate 'mean' on strings
    common_numeric_cols = train_df.select_dtypes(include=[np.number]).columns.intersection(
                          log_df.select_dtypes(include=[np.number]).columns)
    if len(common_numeric_cols)==0:
        print("Warning: no numeric columns found for drift detection")
        return{}

    # for col in train_df.columns:

    #     if col not in log_df.columns:
    #         continue

    #     train_mean = train_df[col].mean()
    #     log_mean = log_df[col].mean()

    #     if train_mean == 0:
    #         percent_shift = 0
    #     else:
    #         percent_shift = abs(log_mean - train_mean) / abs(train_mean)

    #     drift_flag = percent_shift > DRIFT_THRESHOLD

    #     drift_results[col] = {
    #         "train_mean": float(train_mean),
    #         "current_mean": float(log_mean),
    #         "percent_shift": float(percent_shift),
    #         "drift_detected": bool(drift_flag)
    #     }

    # return drift_results
    for col in common_numeric_cols:
            train_mean = train_df[col].mean()
            log_mean = log_df[col].mean()

            if train_mean == 0:
                percent_shift = 0.0 if log_mean == 0 else 1.0
            else:
                percent_shift = abs(log_mean - train_mean) / abs(train_mean)

            drift_flag = percent_shift > DRIFT_THRESHOLD

            drift_results[col] = {
                "train_mean": float(train_mean),
                "current_mean": float(log_mean),
                "percent_shift": float(percent_shift),
                "drift_detected": bool(drift_flag)
            }

    return drift_results

# ---------------- SUMMARY ---------------- #

def generate_summary(drift_results):
    if not drift_results:
        return{"error":"no numeric features to check"}

    total_features = len(drift_results)
    drifted_features = sum(
        1 for v in drift_results.values() if v["drift_detected"]
    )

    summary = {
        "total_features_checked": total_features,
        "features_with_drift": drifted_features,
        "drift_percentage": float(drifted_features / total_features) if total_features > 0 else 0
    }

    return summary


# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    print("Checking data drift...")

    train_df, log_df = load_data()
    if train_df is not None and log_df is not None:
        drift_results = calculate_drift(train_df, log_df)

        summary = generate_summary(drift_results)

        final_report = {
            "summary": summary,
            "feature_drift_details": drift_results
        }

        os.makedirs("src/monitoring", exist_ok=True)

        with open(OUTPUT_PATH, "w") as f:
            json.dump(final_report, f, indent=4)

        print("Drift check completed.Report saved to {OUTPUT_PATH}")
        print("Drift summary:",summary)
    else:
        print("drift check skipped due to missing data")
    
