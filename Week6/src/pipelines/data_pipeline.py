import pandas as pd  
import numpy as np


def load_data(path): #file load kr rhe hai. 
    #def is used to define function. if not used then sara code is in linear format and reusable structure nh bnta. 
    # path se we get to know ki function flexible hai and hardcoded kisi file pr dependent nh hai.
    return pd.read_csv(path) # file ki value ko return kr rha hai. agr return nh kiya toh df none ho jayega.
            #pd.read_csv -> csv file ko dataframe mein convert krta hai without this raw text milega and df operations use hi nh kr skte. 


def clean_data(df): #cleaning function create kiya hai jisme df as a input pass kra rhe hai.
  
    df = df.drop_duplicates() #exact duplicate rows ko remove krta hai if not done toh model biased ho skta hai and same sample multiple times train ho skta hai. 
    # "df=" is an imp step qk agr yeh nh kiya toh original df change nh hoga. drop_duplicates new dataframe return krta hai and if df.drop_duplicates likha toh original df change hi nh hoga. 

    
    if "Date" in df.columns: #hmare dataset mein date ka ek column hai but woh as a string read hogi because of csv file. toh uso datetime object mein convert krne k liye we use this.
        # agr nh kiya toh date sorting incorrect hogi and time-based operations fail ho jayengi.
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce") # yeh coerce se hm system ko bta rhe hai ki agr invalid date mile toh na crash kre na error de bs NaT which is missing date daal de. if not done then program crash ho skta hai.

    # Drop rows where location data is missing
    location_cols = ["Latitude", "Longitude"]
    for col in location_cols:
        if col in df.columns:
            df = df.dropna(subset=[col]) #dropna missing rows ko remove krta hai.
                                         #subset tells ki sirf specific columns check kro. without subset kisi bh column mein koi bh missing value ho toh row delete.

    # Numerical columns -> median
    numerical_cols = df.select_dtypes(include=np.number).columns  #select_dtypes automatically numeric columns ko detect krta hai
                                                                  # include=np.number se hm keh rhe hai ki sirf numbers pick kro. without this object column pr bh median apply ho jayega and then error throw.
    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # Categorical columns -> mode
    categorical_cols = df.select_dtypes(include="object").columns
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])


    outlier_cols = ["Value"]  # Only apply where meaningful

    for col in outlier_cols:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)  #25th percentile
            Q3 = df[col].quantile(0.75)  #75th percentile
            IQR = Q3 - Q1

            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR

            df = df[(df[col] >= lower) & (df[col] <= upper)]

    return df


def save_data(df, path):
    #Save cleaned data
    df.to_csv(path, index=False)  #agr index ko false nh kiya toh ek extra unnamed col create ho jata hai.


if __name__ == "__main__":

    raw_path = "data/raw/Border_Crossing_Entry_Data.csv"
    processed_path = "data/processed/final.csv"

    df = load_data(raw_path)
    df = clean_data(df)
    save_data(df, processed_path)

    print("Data pipeline executed successfully.")
