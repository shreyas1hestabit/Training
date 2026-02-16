import pandas as pd
import json

from sklearn.ensemble import RandomForestClassifier


def select_features(X_train, y_train, top_k=20):

    model = RandomForestClassifier(
        class_weight="balanced",
        random_state=42
    )

    model.fit(X_train, y_train)

    importances = model.feature_importances_

    feature_importance_df = pd.DataFrame({
        "Feature": X_train.columns,
        "Importance": importances
    }).sort_values("Importance", ascending=False)

    selected_features = feature_importance_df["Feature"].head(top_k).tolist()

    return selected_features


if __name__ == "__main__":

    # Assume you saved engineered X_train somewhere
    X_train = pd.read_csv("data/processed/X_train.csv")
    y_train = pd.read_csv("data/processed/y_train.csv")

    selected_features = select_features(X_train, y_train.values.ravel())

    with open("features/selected_feature_list.json", "w") as f:
        json.dump(selected_features, f, indent=4)

    print("Feature selection completed.")
