# # import pandas as pd
# # import json

# # from sklearn.ensemble import RandomForestClassifier


# # def select_features(X_train, y_train, top_k=20):

# #     model = RandomForestClassifier(
# #         class_weight="balanced",
# #         random_state=42
# #     )

# #     model.fit(X_train, y_train)

# #     importances = model.feature_importances_

# #     feature_importance_df = pd.DataFrame({
# #         "Feature": X_train.columns,
# #         "Importance": importances
# #     }).sort_values("Importance", ascending=False)

# #     selected_features = feature_importance_df["Feature"].head(top_k).tolist()

# #     return selected_features


# # if __name__ == "__main__":

# #     # Assume you saved engineered X_train somewhere
# #     X_train = pd.read_csv("data/processed/X_train.csv")
# #     y_train = pd.read_csv("data/processed/y_train.csv")

# #     selected_features = select_features(X_train, y_train.values.ravel())

# #     with open("features/selected_feature_list.json", "w") as f:
# #         json.dump(selected_features, f, indent=4)

# #     print("Feature selection completed.")

# import pandas as pd
# import json
# import os

# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import StandardScaler
# import joblib


# def select_features(X_train, y_train, top_k=20):
#     """
#     Select top k features using Random Forest feature importance
#     """
#     model = RandomForestClassifier(
#         n_estimators=100,
#         class_weight="balanced",
#         random_state=42,
#         n_jobs=-1  # Use all CPU cores for faster training
#     )

#     print(f"Training Random Forest on {X_train.shape[1]} features...")
#     model.fit(X_train, y_train)

#     importances = model.feature_importances_

#     feature_importance_df = pd.DataFrame({
#         "Feature": X_train.columns,
#         "Importance": importances
#     }).sort_values("Importance", ascending=False)

#     print("\nTop 20 Most Important Features:")
#     print(feature_importance_df.head(20))

#     selected_features = feature_importance_df["Feature"].head(top_k).tolist()

#     return selected_features, feature_importance_df


# def save_selected_data(X_train_select, X_test_select, y_train_select, y_test_select):
#     """
#     Save the filtered datasets with selected features
#     """
#     os.makedirs("data/processed", exist_ok=True)

#     X_train_select.to_csv("data/processed/X_train_selected.csv", index=False)
#     X_test_select.to_csv("data/processed/X_test_selected.csv", index=False)
#     y_train_select.to_csv("data/processed/y_train_selected.csv", index=False)
#     y_test_select.to_csv("data/processed/y_test_selected.csv", index=False)

#     print("\n✓ Selected feature datasets saved!")


# if __name__ == "__main__":

#     # Load the already split data from build_features.py
#     print("Loading pre-split data...")
#     X_train = pd.read_csv("data/processed/X_train.csv")
#     X_test = pd.read_csv("data/processed/X_test.csv")
#     y_train = pd.read_csv("data/processed/y_train.csv")
#     y_test = pd.read_csv("data/processed/y_test.csv")

#     print(f"Original X_train shape: {X_train.shape}")
#     print(f"Original X_test shape: {X_test.shape}")

#     # Perform feature selection on training data
#     selected_features, feature_importance_df = select_features(
#         X_train, 
#         y_train.values.ravel(), 
#         top_k=20
#     )

#     # Save selected features list
#     os.makedirs("features", exist_ok=True)
#     with open("features/selected_feature_list.json", "w") as f:
#         json.dump(selected_features, f, indent=4)

#     # Save full feature importance report
#     feature_importance_df.to_csv("features/feature_importance_report.csv", index=False)

#     print(f"\nSelected {len(selected_features)} features:")
#     print(selected_features)

#     # Filter both train and test sets to only include selected features
#     X_train_select = X_train[selected_features].copy()
#     X_test_select = X_test[selected_features].copy()
    
#     # y remains the same
#     y_train_select = y_train
#     y_test_select = y_test


#     print("\nScaling selected features...")
#     scaler = StandardScaler()
    
#     X_train_select_scaled = scaler.fit_transform(X_train_select)
#     X_test_select_scaled = scaler.transform(X_test_select)
    
#     # Convert back to DataFrame
#     X_train_select = pd.DataFrame(
#         X_train_select_scaled, 
#         columns=selected_features,
#         index=X_train_select.index
#     )
#     X_test_select = pd.DataFrame(
#         X_test_select_scaled, 
#         columns=selected_features,
#         index=X_test_select.index
#     )

#     # Save the scaler for later use
#     os.makedirs("models", exist_ok=True)
#     joblib.dump(scaler, "models/scaler.pkl")
#     print(" Scaler saved to models/scaler.pkl")



#     print(f"\nFiltered X_train shape: {X_train_select.shape}")
#     print(f"Filtered X_test shape: {X_test_select.shape}")

#     # Save the filtered datasets
#     save_selected_data(X_train_select, X_test_select, y_train_select, y_test_select)

#     print("\n Feature selection completed successfully!")

import pandas as pd
import json
import os
from sklearn.ensemble import RandomForestClassifier


# ---------------- FEATURE SELECTION ---------------- #

def select_features(X_train, y_train, importance_threshold=0.01):
    """
    Select features based on Random Forest importance threshold
    """

    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    print(f"\nTraining Random Forest on {X_train.shape[1]} features...")
    model.fit(X_train, y_train)

    importances = model.feature_importances_

    feature_importance_df = pd.DataFrame({
        "Feature": X_train.columns,
        "Importance": importances
    }).sort_values("Importance", ascending=False)

    print("\nTop 15 Features:")
    print(feature_importance_df.head(15))

    # Threshold based filtering (more intelligent than fixed top_k)
    selected_features = feature_importance_df[
        feature_importance_df["Importance"] > importance_threshold
    ]["Feature"].tolist()

    print(f"\nSelected {len(selected_features)} features (importance > {importance_threshold})")

    return selected_features, feature_importance_df


# ---------------- SAVE ---------------- #

def save_selected_data(X_train_select, X_test_select, y_train, y_test):

    os.makedirs("data/processed", exist_ok=True)

    X_train_select.to_csv("data/processed/X_train_selected.csv", index=False)
    X_test_select.to_csv("data/processed/X_test_selected.csv", index=False)
    y_train.to_csv("data/processed/y_train_selected.csv", index=False)
    y_test.to_csv("data/processed/y_test_selected.csv", index=False)

    print("\n Selected datasets saved!")


# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    print("Loading split data...")
    X_train = pd.read_csv("data/processed/X_train.csv")
    X_test = pd.read_csv("data/processed/X_test.csv")
    y_train = pd.read_csv("data/processed/y_train.csv")
    y_test = pd.read_csv("data/processed/y_test.csv")

    print(f"Original X_train shape: {X_train.shape}")
    print(f"Original X_test shape: {X_test.shape}")

    selected_features, feature_importance_df = select_features(
        X_train,
        y_train.values.ravel(),
        importance_threshold=0.015
    )

    # Save selected feature list
    os.makedirs("features", exist_ok=True)

    with open("features/selected_feature_list.json", "w") as f:
        json.dump(selected_features, f, indent=4)

    # Save full importance report
    feature_importance_df.to_csv(
        "features/feature_importance_report.csv",
        index=False
    )

    print(f"\nSelected Features:")
    print(selected_features)

    # Filter datasets
    X_train_select = X_train[selected_features].copy()
    X_test_select = X_test[selected_features].copy()

    print(f"\nFiltered X_train shape: {X_train_select.shape}")
    print(f"Filtered X_test shape: {X_test_select.shape}")

    save_selected_data(X_train_select, X_test_select, y_train, y_test)

    print("\n Feature selection completed successfully!")

