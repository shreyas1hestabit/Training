import pandas as pd
from features.build_features import load_data, engineer_features, split_data

df = load_data("data/processed/final.csv")
df = engineer_features(df)

X_train, X_test, y_train, y_test = split_data(df)

print("X_train:", X_train.shape)
print("X_test:", X_test.shape)

print(df.columns.tolist())
print([repr(c) for c in df.columns])  # show exact chars
