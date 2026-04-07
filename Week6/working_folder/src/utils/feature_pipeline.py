
# import pandas as pd
# import numpy as np
# import json
# import joblib
# import os
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import StandardScaler

# class FeaturePipeline:
#     """
#     Complete feature preprocessing pipeline
#     Ensures SAME transformations in training and deployment
#     """
    
#     def __init__(self):
#         self.imputer = None
#         self.scaler = None
#         self.aggregation_stats = None
#         self.selected_features = None
#         self.encoder = None
    
#     def fit(self, X, aggregation_stats_path, selected_features):
#         """
#         Fit imputer and scaler on training data
        
#         Args:
#             X: Training features (after feature engineering & selection)
#             aggregation_stats_path: Path to aggregation stats JSON
#             selected_features: List of selected feature names
#         """
#         # Load aggregation stats
#         with open(aggregation_stats_path, 'r') as f:
#             self.aggregation_stats = json.load(f)
        
#         self.selected_features = selected_features
        
#         # Fit imputer
#         self.imputer = SimpleImputer(strategy="median")
#         X_imputed = self.imputer.fit_transform(X)
        
#         # Fit scaler (optional - only if you scaled during training)
#         # Check your train.py - HistGradientBoosting doesn't need scaling!
#         # But if you used it, uncomment:
#         # self.scaler = StandardScaler()
#         # self.scaler.fit(X_imputed)
        
#         print(f" Pipeline fitted on {X.shape[0]} samples, {X.shape[1]} features")
#         return self
    
#     def transform(self, X):
#         """
#         Transform features using fitted imputer/scaler
        
#         Args:
#             X: Features to transform (DataFrame)
        
#         Returns:
#             Transformed features (DataFrame)
#         """
#         if self.imputer is None:
#             raise ValueError("Pipeline not fitted! Call fit() first")
        
#         # Impute
#         X_imputed = self.imputer.transform(X)
#         X_imputed = pd.DataFrame(X_imputed, columns=X.columns, index=X.index)
        
#         # Scale (if scaler exists)
#         if self.scaler is not None:
#             X_scaled = self.scaler.transform(X_imputed)
#             X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
#             return X_scaled
        
#         return X_imputed
    
#     def save(self, path):
#         """Save pipeline to disk"""
#         os.makedirs(os.path.dirname(path), exist_ok=True)
#         joblib.dump(self, path)
#         print(f" Pipeline saved to {path}")
    
#     @staticmethod
#     def load(path):
#         """Load pipeline from disk"""
#         pipeline = joblib.load(path)
#         print(f" Pipeline loaded from {path}")
#         return pipeline

import pandas as pd
import numpy as np
import json
import joblib
import os
from sklearn.impute import SimpleImputer

class FeaturePipeline:
    def __init__(self):
        self.imputer = None
        self.aggregation_stats = None
        self.selected_features = None
    
    def fit(self, X, aggregation_stats_path, selected_features):
        with open(aggregation_stats_path, 'r') as f:
            self.aggregation_stats = json.load(f)
        
        self.selected_features = selected_features
        self.imputer = SimpleImputer(strategy="median")
        self.imputer.fit(X)
        return self
    
    def transform(self, X):
        if self.imputer is None:
            raise ValueError("Pipeline not fitted!")
        X_imputed = self.imputer.transform(X)
        return pd.DataFrame(X_imputed, columns=X.columns, index=X.index)
    
    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path):
        return joblib.load(path)