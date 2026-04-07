
# import pandas as pd
# import numpy as np
# import json
# import joblib
# import os
# import sys

# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.insert(0, PROJECT_ROOT)

# # ---------------- LOAD RESOURCES ---------------- #
# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# #sys.path.insert(0, os.path.dirname(BASE_DIR))
# ENCODER_PATH = os.path.join(BASE_DIR, "models", "encoder.pkl")
# FEATURE_PIPELINE_PATH = os.path.join(BASE_DIR, "models", "feature_pipeline.pkl")
# # AGGREGATION_STATS_PATH = os.path.join(BASE_DIR, "models", "aggregation_stats.json")

# # Load at module level (once)
# encoder = joblib.load(ENCODER_PATH)

# # with open(SELECTED_FEATURES_PATH, 'r') as f:
# #     selected_features = json.load(f)

# # with open(AGGREGATION_STATS_PATH, 'r') as f:
# #     aggregation_stats = json.load(f)

# from src.utils.feature_pipeline import FeaturePipeline
# feature_pipeline = FeaturePipeline.load(FEATURE_PIPELINE_PATH)
# # print(f" Loaded encoder, {len(selected_features)} selected features, and aggregation stats")
# print("loaded encoder and feature pipeline")


# # ---------------- FEATURE ENGINEERING ---------------- #

# def engineer_features(df):
#     """
#     Apply SAME feature engineering as training
#     Uses user input + saved aggregation statistics
#     """
#     df = df.copy()
#     df.columns = df.columns.str.strip()

#     # ---------------- Date Features ---------------- #
#     df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
#     df["Month"] = df["Date"].dt.month
#     df["Quarter"] = df["Date"].dt.quarter
#     df["Day_of_Week"] = df["Date"].dt.dayofweek

#     # ---------------- Aggregation Features (FROM SAVED STATS) ---------------- #

#     aggregation_stats = feature_pipeline.aggregation_stats
    
#     # Calculate global defaults
#     GLOBAL_DEFAULTS = {
#         "Port_Avg_Value": sum(aggregation_stats["Port_Avg_Value"].values()) / len(aggregation_stats["Port_Avg_Value"]),
#         "Port_Max_Value": sum(aggregation_stats["Port_Max_Value"].values()) / len(aggregation_stats["Port_Max_Value"]),
#         "Measure_Avg_Value": sum(aggregation_stats["Measure_Avg_Value"].values()) / len(aggregation_stats["Measure_Avg_Value"]),
#         "Border_Avg_Value": sum(aggregation_stats["Border_Avg_Value"].values()) / len(aggregation_stats["Border_Avg_Value"]),
#         "Month_Avg_Value": sum(aggregation_stats["Month_Avg_Value"].values()) / len(aggregation_stats["Month_Avg_Value"])
#     }
    
#     # Port features - lookup from saved stats
#     # df["Port_Avg_Value"] = df["Port Name"].map(
#     #     aggregation_stats["Port_Avg_Value"]
#     # ).fillna(
#     #     # Default: overall average if port not seen in training
#     #     sum(aggregation_stats["Port_Avg_Value"].values()) / 
#     #     len(aggregation_stats["Port_Avg_Value"])
#     # )
    
#     # df["Port_Max_Value"] = df["Port Name"].map(
#     #     aggregation_stats["Port_Max_Value"]
#     # ).fillna(
#     #     sum(aggregation_stats["Port_Max_Value"].values()) / 
#     #     len(aggregation_stats["Port_Max_Value"])
#     # )
    
#     # # Measure features - lookup from saved stats
#     # df["Measure_Avg_Value"] = df["Measure"].map(
#     #     aggregation_stats["Measure_Avg_Value"]
#     # ).fillna(
#     #     sum(aggregation_stats["Measure_Avg_Value"].values()) / 
#     #     len(aggregation_stats["Measure_Avg_Value"])
#     # )
    
#     # # Border features - lookup from saved stats
#     # df["Border_Avg_Value"] = df["Border"].map(
#     #     aggregation_stats["Border_Avg_Value"]
#     # ).fillna(
#     #     sum(aggregation_stats["Border_Avg_Value"].values()) / 
#     #     len(aggregation_stats["Border_Avg_Value"])
#     # )

#     df["Port_Avg_Value"] = df["Port Name"].map(
#         aggregation_stats["Port_Avg_Value"]
#     ).fillna(GLOBAL_DEFAULTS["Port_Avg_Value"])
    
#     df["Port_Max_Value"] = df["Port Name"].map(
#         aggregation_stats["Port_Max_Value"]
#     ).fillna(GLOBAL_DEFAULTS["Port_Max_Value"])
    
#     # Measure features
#     df["Measure_Avg_Value"] = df["Measure"].map(
#         aggregation_stats["Measure_Avg_Value"]
#     ).fillna(GLOBAL_DEFAULTS["Measure_Avg_Value"])
    
#     # Border features
#     df["Border_Avg_Value"] = df["Border"].map(
#         aggregation_stats["Border_Avg_Value"]
#     ).fillna(GLOBAL_DEFAULTS["Border_Avg_Value"])
    
#     # Month features - lookup from saved stats
#     # df["Month_Avg_Value"] = df["Month"].map(
#     #     {int(k): v for k, v in aggregation_stats["Month_Avg_Value"].items()}
#     # ).fillna(
#     #     sum(aggregation_stats["Month_Avg_Value"].values()) / 
#     #     len(aggregation_stats["Month_Avg_Value"])
#     # )
#     month_mapping = {int(k): v for k, v in aggregation_stats["Month_Avg_Value"].items()}
#     df["Month_Avg_Value"] = df["Month"].map(month_mapping).fillna(
#         GLOBAL_DEFAULTS["Month_Avg_Value"]
#     )

#     # ---------------- Drop Unnecessary Columns ---------------- #
#     df = df.drop(columns=["Date", "Port Code", "Port Name"], errors="ignore")
    
#     return df


# # ---------------- CATEGORICAL ENCODING ---------------- #

# def encode_categorical(df):
#     """
#     OneHot encode categorical columns using TRAINED encoder
#     """
#     categorical_cols = ["State", "Border", "Measure"]
    
#     # Check if columns exist
#     missing_cols = [col for col in categorical_cols if col not in df.columns]
#     if missing_cols:
#         raise ValueError(f"Missing required columns: {missing_cols}")
    
#     for col in categorical_cols:
#         if df[col].isna().any():
#             df[col].fillna("Unknown", inplace=True)
    
#     # Encode using TRAINED encoder
#     encoded = encoder.transform(df[categorical_cols])
    
#     # Convert sparse matrix to DataFrame
#     encoded_df = pd.DataFrame.sparse.from_spmatrix(
#         encoded,
#         columns=encoder.get_feature_names_out(categorical_cols),
#         index=df.index
#     )
    
#     # Drop original categorical columns
#     df = df.drop(columns=categorical_cols)
    
#     # Concatenate encoded features
#     df = pd.concat([df, encoded_df], axis=1)
    
#     return df


# # ---------------- MAIN PREPROCESSING PIPELINE ---------------- #

# def preprocess_input(raw_input):
  
#     # # Step 1: Convert to DataFrame
#     # df = pd.DataFrame([raw_input])
    
#     # print(f"Input columns: {df.columns.tolist()}")
    
#     # # Step 2: Feature Engineering (creates aggregation features)
#     # df = engineer_features(df)
    
#     # print(f"After feature engineering: {df.shape} - {df.columns.tolist()}")
    
#     # # Step 3: OneHot Encoding
#     # df = encode_categorical(df)
    
#     # print(f"After encoding: {df.shape}")
    
#     # # Step 4: Ensure ALL selected features exist
#     # # Add missing features with 0 (for OneHot columns not present)
#     # for feat in selected_features:
#     #     if feat not in df.columns:
#     #         df[feat] = 0
    
#     # # Step 5: Keep ONLY selected features in CORRECT order
#     # df = df[selected_features]
    
#     # print(f"Final shape: {df.shape}")
#     # print(f"Final features: {df.columns.tolist()}")
    
#     # return df
#     required_fields = ["Port Name", "State", "Border", "Date", "Measure", "Latitude", "Longitude"]
#     missing = [f for f in required_fields if f not in raw_input]
#     if missing:
#         raise ValueError(f"Missing required input fields: {missing}")
    
#     if raw_input.get("Latitude") is None:
#         raw_input["Latitude"] = 0
#     if raw_input.get("Longitude") is None:
#         raw_input["Longitude"] = 0
    
#     df = pd.DataFrame([raw_input])
    
#     # Feature Engineering
#     df = engineer_features(df)
    
#     # OneHot Encoding
#     df = encode_categorical(df)
    
#     # Ensure all selected features exist
#     for feat in feature_pipeline.selected_features:
#         if feat not in df.columns:
#             df[feat] = 0
    
#     # Keep only selected features
#     df = df[feature_pipeline.selected_features]
    
#     #  CRITICAL: Use SAME imputation as training!
#     df = feature_pipeline.transform(df)
    
#     print(f"Final preprocessed shape: {df.shape}")
    
#     return df



import os
import joblib
import pandas as pd
from src.utils.feature_pipeline import FeaturePipeline

# Path logic relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENCODER_PATH = os.path.join(BASE_DIR, "models", "encoder.pkl")
PIPELINE_PATH = os.path.join(BASE_DIR, "models", "feature_pipeline.pkl")

# Load assets once
encoder = joblib.load(ENCODER_PATH)
feature_pipeline = FeaturePipeline.load(PIPELINE_PATH)

def engineer_features(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.month
    df["Quarter"] = df["Date"].dt.quarter
    df["Day_of_Week"] = df["Date"].dt.dayofweek

    stats = feature_pipeline.aggregation_stats
    
    # Map aggregation stats (Use 0 or global mean as fallback)
    df["Port_Avg_Value"] = df["Port Name"].map(stats["Port_Avg_Value"]).fillna(0)
    df["Port_Max_Value"] = df["Port Name"].map(stats["Port_Max_Value"]).fillna(0)
    df["Measure_Avg_Value"] = df["Measure"].map(stats["Measure_Avg_Value"]).fillna(0)
    df["Border_Avg_Value"] = df["Border"].map(stats["Border_Avg_Value"]).fillna(0)
    #df["Month_Avg_Value"] = df["Month"].map(stats["Month_Avg_Value"]).fillna(0)
    month_mapping = {int(k): v for k, v in stats["Month_Avg_Value"].items()}
    df["Month_Avg_Value"] = df["Month"].astype(int).map(month_mapping).fillna(0)
#check if this code line works correctly or not
    df = df.drop(columns=["Date", "Port Name", "Port Code"], errors="ignore")
    
    return df

def preprocess_input(raw_input):
    df = pd.DataFrame([raw_input])
    df = engineer_features(df)
    
    # One-Hot Encoding
    cat_cols = ["State", "Border", "Measure"]
    encoded = encoder.transform(df[cat_cols])
    encoded_df = pd.DataFrame.sparse.from_spmatrix(
        encoded, columns=encoder.get_feature_names_out(cat_cols), index=df.index
    )
    
    # Merge and Drop
    df = pd.concat([df.drop(columns=cat_cols), encoded_df], axis=1)
    
    # CRITICAL: Keep ONLY selected features in correct order
    for feat in feature_pipeline.selected_features:
        if feat not in df.columns:
            df[feat] = 0
            
    df = df[feature_pipeline.selected_features]
    
    # Apply Imputation
    return feature_pipeline.transform(df)