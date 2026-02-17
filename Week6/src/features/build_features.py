# # # import pandas as pd
# # # import numpy as np
# # # import os 
# # # import json
# # # from sklearn.model_selection import train_test_split
# # # from sklearn.preprocessing import OneHotEncoder, StandardScaler
# # # def load_data(path):
# # #     return pd.read_csv(path)

# # # def engineer_features(df):
# # #     df=df.drop(columns=["Value"], errors="ignore")
# # #     df["Date"]=pd.to_datetime(df["Date"])
# # #     df["Year"]=df["Date"].dt.year
# # #     df["Month"]=df["Date"].dt.month
# # #     df["Quarter"]=df["Date"].dt.quarter
# # #     df["Is_month_start"]=df["Date"].dt.is_month_start.astype(int)
# # #     df["Is_month_end"]=df["Date"].dt.is_month_end.astype(int)
# # #     df=df.drop(columns=["Date"])

# # #     df["Abs_latitude"]=df["Latitude"].abs()
# # #     df["Abs_longitude"]=df["Longitude"].abs()
# # #     df["Lat_Long_Product"]=df["Latitude"]*df["Longitude"]
# # #     df["Lat_Long_Sum"]=df["Latitude"]+df["Longitude"]

# # #     df["is_canada_border"]=(
# # #         df["Border"]=="US-Canada Border"
# # #     ).astype(int)
# # #     return df

# # # def split_data(df):
# # #     y=df["Traffic_level"]
# # #     x= df.drop(columns=["Traffic_level"])
# # #     X_train, X_test, y_train, y_test = train_test_split(
# # #         x,y,
# # #         test_size=0.2,
# # #         random_state=42,
# # #         stratify=y
# # #     )

# # #     return X_train, X_test, y_train, y_test


# # # def encode_and_scale(X_train, X_test):

# # #     categorical_cols = X_train.select_dtypes(
# # #         include=["object", "category"]
# # #     ).columns

# # #     encoder = OneHotEncoder(
# # #         handle_unknown="ignore",
# # #         sparse=False
# # #     )

# # #     encoded_train = encoder.fit_transform(
# # #         X_train[categorical_cols]
# # #     )

# # #     encoded_test = encoder.transform(
# # #         X_test[categorical_cols]
# # #     )

# # #     encoded_train_df = pd.DataFrame(
# # #         encoded_train,
# # #         columns=encoder.get_feature_names_out(categorical_cols),
# # #         index=X_train.index
# # #     )

# # #     encoded_test_df = pd.DataFrame(
# # #         encoded_test,
# # #         columns=encoder.get_feature_names_out(categorical_cols),
# # #         index=X_test.index
# # #     )

# # #     X_train = X_train.drop(columns=categorical_cols)
# # #     X_test = X_test.drop(columns=categorical_cols)

# # #     X_train = pd.concat([X_train, encoded_train_df], axis=1)
# # #     X_test = pd.concat([X_test, encoded_test_df], axis=1)

# # #     # Scaling
# # #     num_cols = X_train.select_dtypes(include=np.number).columns

# # #     scaler = StandardScaler()

# # #     X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
# # #     X_test[num_cols] = scaler.transform(X_test[num_cols])

# # #     return X_train, X_test, y_train, y_test


# # # if __name__ == "__main__":

# # #     data_path = "data/processed/final.csv"

# # #     df = load_data(data_path)

# # #     df = engineer_features(df)

# # #     X_train, X_test, y_train, y_test = split_data(df)

# # #     X_train, X_test = encode_and_scale(X_train, X_test)

# # #     print("Feature engineering completed.")

# # import pandas as pd
# # import numpy as np
# # import os
# # import json
# # from sklearn.model_selection import train_test_split
# # from sklearn.preprocessing import OneHotEncoder, StandardScaler


# # # ---------------- LOAD ---------------- #

# # def load_data(path):
# #     df= pd.read_csv(path)
# #     df.columns=df.columns.str.strip()
# #     return df


# # def stratified_sampling(df, max_per_class=50000):

# #     # df_sampled = (
# #     #     df.groupby("Traffic_level", group_keys=False)
# #     #     .apply(lambda x: x.sample(min(len(x), max_per_class), random_state=42))
# #     #     .reset_index(drop=True)
# #     # )
# #     if "Traffic_level" not in df.columns:
# #         raise ValueError(f"Traffic_level column missing! Columns: {df.columns.tolist()}")
    
# #     df_sampled = df.groupby("Traffic_level", group_keys=False).apply(
# #         lambda x: x.sample(min(len(x), max_per_class), random_state=42)
# #     ).reset_index(drop=True)

# #     return df_sampled

# # # ---------------- FEATURE ENGINEERING ---------------- #

# # def engineer_features(df):

# #     df.columns= df.columns.str.strip()

# #     # Target leakage avoid
# #     df = df.drop(columns=["Value"], errors="ignore")

# #     # ----- Date Features -----
# #     df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# #     df["Year"] = df["Date"].dt.year
# #     df["Month"] = df["Date"].dt.month
# #     df["Quarter"] = df["Date"].dt.quarter
# #     df["Day"] = df["Date"].dt.day
# #     df["Day_of_Week"] = df["Date"].dt.dayofweek
# #     df["Is_month_start"] = df["Date"].dt.is_month_start.astype(int)
# #     df["Is_month_end"] = df["Date"].dt.is_month_end.astype(int)

# #     df = df.drop(columns=["Date"])

# #     # ----- Geo Features -----
# #     df["Abs_latitude"] = df["Latitude"].abs()
# #     df["Abs_longitude"] = df["Longitude"].abs()
# #     df["Lat_Long_Product"] = df["Latitude"] * df["Longitude"]
# #     df["Lat_Long_Sum"] = df["Latitude"] + df["Longitude"]
# #     df["Lat_Long_Diff"] = df["Latitude"] - df["Longitude"]

# #     # ----- Border Binary Feature -----
# #     df["is_canada_border"] = (
# #         df["Border"] == "US-Canada Border"
# #     ).astype(int)

# #     df=df.drop(columns=["Port Name", "Port Code"], errors="ignore")

# #     return df


# # # ---------------- SPLIT ---------------- #

# # # def split_data(df):

# # #     y = df["Traffic_level"]
# # #     X = df.drop(columns=["Traffic_level"])

# # #     X_train, X_test, y_train, y_test = train_test_split(
# # #         X,
# # #         y,
# # #         test_size=0.2,
# # #         random_state=42,
# # #         stratify=y
# # #     )

# # #     return X_train, X_test, y_train, y_test

# # # ---------------- SPLIT ---------------- #

# # def split_data(df, target_col='Traffic_level'):
# #     """Split data ensuring target column exists"""
    
# #     if target_col not in df.columns:
# #         raise ValueError(f"Target column '{target_col}' not found! Available columns: {df.columns.tolist()}")
    
# #     y = df[target_col]
# #     X = df.drop(columns=[target_col])

# #     X_train, X_test, y_train, y_test = train_test_split(
# #         X,
# #         y,
# #         test_size=0.2,
# #         random_state=42,
# #         stratify=y
# #     )

# #     return X_train, X_test, y_train, y_test


# # # ---------------- ENCODE + SCALE ---------------- #

# # def encode_and_scale(X_train, X_test):

# #     categorical_cols = ["State","Border","Measure"]

# #     # Updated sklearn parameter
# #     encoder = OneHotEncoder(
# #         handle_unknown="ignore",
# #         sparse_output=True
# #     )

# #     encoded_train = encoder.fit_transform(
# #         X_train[categorical_cols]
# #     )

# #     encoded_test = encoder.transform(
# #         X_test[categorical_cols]
# #     )

# #     encoded_train_df = pd.DataFrame(
# #         encoded_train,
# #         columns=encoder.get_feature_names_out(categorical_cols),
# #         index=X_train.index
# #     )

# #     encoded_test_df = pd.DataFrame(
# #         encoded_test,
# #         columns=encoder.get_feature_names_out(categorical_cols),
# #         index=X_test.index
# #     )

# #     X_train = X_train.drop(columns=categorical_cols)
# #     X_test = X_test.drop(columns=categorical_cols)

# #     X_train = pd.concat([X_train, encoded_train_df], axis=1)
# #     X_test = pd.concat([X_test, encoded_test_df], axis=1)

# #     # ----- Scaling -----
# #     num_cols = X_train.select_dtypes(include=np.number).columns

# #     scaler = StandardScaler()

# #     X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
# #     X_test[num_cols] = scaler.transform(X_test[num_cols])

# #     return X_train, X_test


# # # ---------------- SAVE ---------------- #

# # def save_split_data(X_train, X_test, y_train, y_test):

# #     os.makedirs("data/processed", exist_ok=True)

# #     X_train.to_csv("data/processed/X_train.csv", index=False)
# #     X_test.to_csv("data/processed/X_test.csv", index=False)
# #     y_train.to_csv("data/processed/y_train.csv", index=False)
# #     y_test.to_csv("data/processed/y_test.csv", index=False)

# #     # Save feature list
# #     feature_list = list(X_train.columns)
# #     os.makedirs("features",exist_ok=True)
# #     with open("features/feature_list.json", "w") as f:
# #         json.dump(feature_list, f, indent=4)


# # # ---------------- MAIN ---------------- #

# # if __name__ == "__main__":

# #     data_path = "data/processed/final.csv"

# #     df = load_data(data_path)

# #     target=df["Traffic_level"].copy()
# #     df = engineer_features(df)
# #     df=stratified_sampling(df,max_per_class=50000)
# #     df["Traffic_level"]=target.loc[df.index]
# #     print("after sampling: ",df.shape)


# #     X_train, X_test, y_train, y_test = split_data(df)

# #     X_train, X_test = encode_and_scale(X_train, X_test)

# #     print("x_train:",X_train.shape)
# #     print("x_test:",X_test.shape)

# #     save_split_data(X_train, X_test, y_train, y_test)

# #     print("Feature engineering + split + encoding completed successfully.")

# import pandas as pd
# import numpy as np
# import os
# import json
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OneHotEncoder, StandardScaler


# # ---------------- LOAD ---------------- #

# def load_data(path):
#     df = pd.read_csv(path)
#     df.columns = df.columns.str.strip()
#     return df


# def stratified_sampling(df, max_per_class=50000):

#     if "Traffic_level" not in df.columns:
#         raise ValueError(f"Traffic_level column missing! Columns: {df.columns.tolist()}")
    
#     # df_sampled = df.groupby("Traffic_level", group_keys=False).apply(
#     #     lambda x: x.sample(min(len(x), max_per_class), random_state=42)
#     # ).reset_index(drop=True)

#     # Use sample on each group and concatenate results
#     sampled_groups = []
#     for name, group in df.groupby("Traffic_level"):
#         sampled_group = group.sample(n=min(len(group), max_per_class), random_state=42)
#         sampled_groups.append(sampled_group)
    
#     df_sampled = pd.concat(sampled_groups, ignore_index=True)

#     return df_sampled

# # ---------------- FEATURE ENGINEERING ---------------- #

# def engineer_features(df):

#     df=df.copy()
#     df.columns = df.columns.str.strip()

#     if "Traffic_level" in df.columns:
#         traffic_level = df["Traffic_level"].copy()
#         df = df.drop(columns=["Traffic_level"])
#     else:
#         traffic_level = None

#     # Target leakage avoid
#     df = df.drop(columns=["Value"], errors="ignore")

#     # ----- Date Features -----
#     df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

#     df["Year"] = df["Date"].dt.year
#     df["Month"] = df["Date"].dt.month
#     df["Quarter"] = df["Date"].dt.quarter
#     df["Day"] = df["Date"].dt.day
#     df["Day_of_Week"] = df["Date"].dt.dayofweek
#     df["Is_month_start"] = df["Date"].dt.is_month_start.astype(int)
#     df["Is_month_end"] = df["Date"].dt.is_month_end.astype(int)

#     df = df.drop(columns=["Date"])

#     # ----- Geo Features -----
#     df["Abs_latitude"] = df["Latitude"].abs()
#     df["Abs_longitude"] = df["Longitude"].abs()
#     df["Lat_Long_Product"] = df["Latitude"] * df["Longitude"]
#     df["Lat_Long_Sum"] = df["Latitude"] + df["Longitude"]
#     df["Lat_Long_Diff"] = df["Latitude"] - df["Longitude"]

#     # ----- Border Binary Feature -----
#     df["is_canada_border"] = (
#         df["Border"] == "US-Canada Border"
#     ).astype(int)

#     df = df.drop(columns=["Port Name", "Port Code"], errors="ignore")

#     if traffic_level is not None:
#         df["Traffic_level"] = traffic_level

#     return df


# # ---------------- SPLIT ---------------- #

# def split_data(df):
#     if "Traffic_level" not in df.columns:
#         raise ValueError(f"Traffic_level column not found! Available columns: {df.columns.tolist()}")
#     y = df["Traffic_level"]
#     X = df.drop(columns=["Traffic_level"])

#     X_train, X_test, y_train, y_test = train_test_split(
#         X,
#         y,
#         test_size=0.2,
#         random_state=42,
#         stratify=y
#     )

#     return X_train, X_test, y_train, y_test


# # ---------------- ENCODE + SCALE ---------------- #

# # def encode_and_scale(X_train, X_test):

# #     categorical_cols = ["State", "Border", "Measure"]

# #     # Keep sparse_output=True for memory efficiency
# #     encoder = OneHotEncoder(
# #         handle_unknown="ignore",
# #         sparse_output=True
# #     )

# #     encoded_train = encoder.fit_transform(
# #         X_train[categorical_cols]
# #     )

# #     encoded_test = encoder.transform(
# #         X_test[categorical_cols]
# #     )

# #     # Convert sparse matrix to DataFrame using pd.arrays.SparseArray
# #     encoded_train_df = pd.DataFrame.sparse.from_spmatrix(
# #         encoded_train,
# #         columns=encoder.get_feature_names_out(categorical_cols),
# #         index=X_train.index
# #     )

# #     encoded_test_df = pd.DataFrame.sparse.from_spmatrix(
# #         encoded_test,
# #         columns=encoder.get_feature_names_out(categorical_cols),
# #         index=X_test.index
# #     )

# #     X_train = X_train.drop(columns=categorical_cols)
# #     X_test = X_test.drop(columns=categorical_cols)

# #     X_train = pd.concat([X_train, encoded_train_df], axis=1)
# #     X_test = pd.concat([X_test, encoded_test_df], axis=1)

# #     # ----- Scaling -----
# #     num_cols = X_train.select_dtypes(include=np.number).columns

# #     scaler = StandardScaler()

# #     X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
# #     X_test[num_cols] = scaler.transform(X_test[num_cols])

# #     return X_train, X_test


# def encode_features(X_train, X_test):
#     categorical_cols = ["State", "Border", "Measure"]

#     encoder = OneHotEncoder(
#         handle_unknown="ignore",
#         sparse_output=True
#     )

#     encoded_train = encoder.fit_transform(X_train[categorical_cols])
#     encoded_test = encoder.transform(X_test[categorical_cols])

#     encoded_train_df = pd.DataFrame.sparse.from_spmatrix(
#         encoded_train,
#         columns=encoder.get_feature_names_out(categorical_cols),
#         index=X_train.index
#     )

#     encoded_test_df = pd.DataFrame.sparse.from_spmatrix(
#         encoded_test,
#         columns=encoder.get_feature_names_out(categorical_cols),
#         index=X_test.index
#     )

#     X_train = X_train.drop(columns=categorical_cols)
#     X_test = X_test.drop(columns=categorical_cols)

#     X_train = pd.concat([X_train, encoded_train_df], axis=1)
#     X_test = pd.concat([X_test, encoded_test_df], axis=1)

#     # NO SCALING HERE!
#     return X_train, X_test


# # ---------------- SAVE ---------------- #

# def save_split_data(X_train, X_test, y_train, y_test):

#     os.makedirs("data/processed", exist_ok=True)

#     X_train.to_csv("data/processed/X_train.csv", index=False)
#     X_test.to_csv("data/processed/X_test.csv", index=False)
#     y_train.to_csv("data/processed/y_train.csv", index=False)
#     y_test.to_csv("data/processed/y_test.csv", index=False)

#     # Save feature list
#     feature_list = list(X_train.columns)
#     os.makedirs("features", exist_ok=True)
#     with open("features/feature_list.json", "w") as f:
#         json.dump(feature_list, f, indent=4)


# # ---------------- MAIN ---------------- #

# if __name__ == "__main__":

#     data_path = "data/processed/final.csv"

#     # df = load_data(data_path)
#     # df = engineer_features(df)
#     # df = stratified_sampling(df, max_per_class=50000)
#     # print("after sampling: ", df.shape)

#     # X_train, X_test, y_train, y_test = split_data(df)

#     # X_train, X_test = encode_and_scale(X_train, X_test)

#     # print("x_train:", X_train.shape)
#     # print("x_test:", X_test.shape)

#     # save_split_data(X_train, X_test, y_train, y_test)

#     # print("Feature engineering + split + encoding completed successfully.")

#     print("Loading data...")
#     df = load_data(data_path)
#     print(f"Loaded data shape: {df.shape}")
#     print(f"Columns after loading: {df.columns.tolist()}")
    
#     print("\nEngineering features...")
#     df = engineer_features(df)
#     print(f"After feature engineering: {df.shape}")
#     print(f"Columns after feature engineering: {df.columns.tolist()}")
    
#     print("\nPerforming stratified sampling...")
#     df = stratified_sampling(df, max_per_class=50000)
#     print(f"After sampling: {df.shape}")
#     print(f"Columns after sampling: {df.columns.tolist()}")

#     X_train, X_test, y_train, y_test = split_data(df)

#     X_train, X_test = encode_features(X_train, X_test)

#     print("\nx_train:", X_train.shape)
#     print("x_test:", X_test.shape)

#     save_split_data(X_train, X_test, y_train, y_test)

#     print("\n Feature engineering + split + encoding completed successfully.")



import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

def load_data(path):
    df=pd.read_csv(path)
    df.columns=df.columns.str.strip()
    return df

def engineer_features(df):
    df=df.copy()
    df.columns=df.columns.str.strip()

    if "Traffic_level" in df.columns:
        traffic_level=df["Traffic_level"].copy()
    else:
        raise ValueError("traffic_level column missing")
    
    df["Date"]=pd.to_datetime(df["Date"], errors="coerce")

    df["Month"] = df["Date"].dt.month
    df["Quarter"] = df["Date"].dt.quarter
    df["Day_of_Week"] = df["Date"].dt.dayofweek
    # df["Is_month_start"] = df["Date"].dt.is_month_start.astype(int)
    # df["Is_month_end"] = df["Date"].dt.is_month_end.astype(int)

    df["Port_Avg_Value"] = df.groupby("Port Name")["Value"].transform("mean")
    df["Port_Max_Value"] = df.groupby("Port Name")["Value"].transform("max")

    df["Measure_Avg_Value"] = df.groupby("Measure")["Value"].transform("mean")

    df["Border_Avg_Value"] = df.groupby("Border")["Value"].transform("mean")

    df["Month_Avg_Value"] = df.groupby("Month")["Value"].transform("mean")

    # df["Abs_latitude"] = df["Latitude"].abs()
    # df["Abs_longitude"] = df["Longitude"].abs()

    df=df.drop(columns=["Value"], errors="ignore")
    df=df.drop(columns=["Date","Port Code"], errors="ignore")
    df=df.drop(columns=["Port Name"], errors="ignore")

    df["Traffic_level"] = traffic_level
    return df

def stratified_sampling(df, max_per_class=50000):

    sampled_groups = []
    for name, group in df.groupby("Traffic_level"):
        sampled_group = group.sample(
            n=min(len(group), max_per_class),
            random_state=42
        )
        sampled_groups.append(sampled_group)

    df_sampled = pd.concat(sampled_groups, ignore_index=True)
    return df_sampled

def split_data(df):

    y = df["Traffic_level"]
    X = df.drop(columns=["Traffic_level"])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    return X_train, X_test, y_train, y_test
def encode_features(X_train, X_test):

    categorical_cols = ["State", "Border", "Measure"]

    encoder = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True
    )

    encoded_train = encoder.fit_transform(X_train[categorical_cols])
    encoded_test = encoder.transform(X_test[categorical_cols])

    encoded_train_df = pd.DataFrame.sparse.from_spmatrix(
        encoded_train,
        columns=encoder.get_feature_names_out(categorical_cols),
        index=X_train.index
    )

    encoded_test_df = pd.DataFrame.sparse.from_spmatrix(
        encoded_test,
        columns=encoder.get_feature_names_out(categorical_cols),
        index=X_test.index
    )

    X_train = X_train.drop(columns=categorical_cols)
    X_test = X_test.drop(columns=categorical_cols)

    X_train = pd.concat([X_train, encoded_train_df], axis=1)
    X_test = pd.concat([X_test, encoded_test_df], axis=1)

    return X_train, X_test


# ---------------- SAVE ---------------- #

def save_split_data(X_train, X_test, y_train, y_test):

    os.makedirs("data/processed", exist_ok=True)

    X_train.to_csv("data/processed/X_train.csv", index=False)
    X_test.to_csv("data/processed/X_test.csv", index=False)
    y_train.to_csv("data/processed/y_train.csv", index=False)
    y_test.to_csv("data/processed/y_test.csv", index=False)

    feature_list = list(X_train.columns)
    os.makedirs("features", exist_ok=True)

    with open("features/feature_list.json", "w") as f:
        json.dump(feature_list, f, indent=4)


# ---------------- MAIN ---------------- #

if __name__ == "__main__":

    data_path = "data/processed/final.csv"

    print("Loading data...")
    df = load_data(data_path)
    print("Original shape:", df.shape)

    print("\nEngineering features...")
    df = engineer_features(df)
    print("After feature engineering:", df.shape)

    print("\nApplying stratified sampling...")
    df = stratified_sampling(df, max_per_class=50000)
    print("After sampling:", df.shape)

    X_train, X_test, y_train, y_test = split_data(df)

    print("\nEncoding features...")
    X_train, X_test = encode_features(X_train, X_test)

    print("X_train shape:", X_train.shape)
    print("X_test shape:", X_test.shape)

    save_split_data(X_train, X_test, y_train, y_test)

    print("\n Feature engineering pipeline completed successfully!")