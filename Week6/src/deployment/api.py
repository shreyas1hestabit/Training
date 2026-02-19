# # import os
# # import uuid
# # import joblib
# # import pandas as pd
# # from fastapi import FastAPI
# # from pydantic import BaseModel
# # from datetime import datetime
# # import json
# # from dotenv import load_dotenv

# # # ---------------- PATH FIX ---------------- #

# # BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
# # # This points to src/
# # load_dotenv()
# # # MODEL_PATH = os.path.join(BASE_DIR, "models", "tuned_model.pkl")
# # MODEL_PATH = os.getenv("MODEL_PATH")
# # FEATURE_PATH = os.path.join(BASE_DIR, "features", "selected_feature_list.json")
# # #LOG_PATH = os.path.join(BASE_DIR, "prediction_logs.csv")
# # LOG_PATH = os.getenv("LOG_PATH")

# # # ---------------- LOAD MODEL ---------------- #

# # model = joblib.load(MODEL_PATH)

# # with open(FEATURE_PATH, "r") as f:
# #     selected_features = json.load(f)

# # # ---------------- FASTAPI APP ---------------- #

# # app = FastAPI(title="Traffic Classification API")

# # # ---------------- INPUT SCHEMA ---------------- #

# # class PredictionInput(BaseModel):
# #     data: dict

# # # ---------------- ROOT ---------------- #

# # @app.get("/")
# # def home():
# #     return {"message": "Traffic Classification API Running "}

# # # ---------------- PREDICT ---------------- #

# # @app.post("/predict")
# # def predict(input_data: PredictionInput):

# #     request_id = str(uuid.uuid4())

# #     # Convert to DataFrame
# #     df = pd.DataFrame([input_data.data])

# #     # Keep only selected features
# #     df = df[selected_features]

# #     prediction = model.predict(df)[0]

# #     # ---------------- LOGGING ---------------- #

# #     log_entry = input_data.data.copy()
# #     log_entry["prediction"] = prediction
# #     log_entry["request_id"] = request_id
# #     log_entry["timestamp"] = datetime.now()

# #     log_df = pd.DataFrame([log_entry])

# #     if os.path.exists(LOG_PATH):
# #         log_df.to_csv(LOG_PATH, mode="a", header=False, index=False)
# #     else:
# #         log_df.to_csv(LOG_PATH, index=False)

# #     return {
# #         "request_id": request_id,
# #         "prediction": prediction
# #     }




# import os
# import uuid
# import joblib
# import pandas as pd
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from datetime import datetime
# from dotenv import load_dotenv

# #  Import preprocessing function
# import sys
# # sys.path.append(os.path.dirname(__file__))
# # from utils.preprocessing import preprocess_input
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.insert(0, PROJECT_ROOT)
# from src.utils.preprocessing import preprocess_input

# # ---------------- PATHS ---------------- #
# # load_dotenv()

# # MODEL_PATH = os.getenv("MODEL_PATH")
# # LOG_PATH = os.getenv("LOG_PATH")

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
# # # This points to src/
# load_dotenv()
# MODEL_PATH = os.path.join(BASE_DIR, "models", "tuned_model.pkl")
# MODEL_PATH = os.getenv("MODEL_PATH")
# FEATURE_PATH = os.path.join(BASE_DIR, "features", "selected_feature_list.json")
# LOG_PATH = os.path.join(BASE_DIR, "prediction_logs.csv")
# LOG_PATH = os.getenv("LOG_PATH")


# # ---------------- LOAD MODEL ---------------- #
# print("Loading model...")
# model = joblib.load(MODEL_PATH)
# print(f" Model loaded: {type(model).__name__}")

# # ---------------- FASTAPI APP ---------------- #
# app = FastAPI(title="Traffic Classification API")

# # ---------------- INPUT SCHEMA ---------------- #
# class PredictionInput(BaseModel):
#     data: dict
    
#     class Config:
#         schema_extra = {
#             "example": {
#                 "data": {
#                     "Port Name": "Buffalo-Niagara Falls",
#                     "State": "New York",
#                     "Border": "US-Canada Border",
#                     "Date": "2024-07-15",
#                     "Measure": "Personal Vehicles",
#                     "Latitude": 42.9,
#                     "Longitude": -78.9
#                 }
#             }
#         }

# # ---------------- ROUTES ---------------- #

# @app.get("/")
# def home():
#     return {
#         "message": "Traffic Classification API Running",
#         "model": type(model).__name__,
#         "status": "healthy"
#     }

# @app.post("/predict")
# def predict(input_data: PredictionInput):
#     try:
#         request_id = str(uuid.uuid4())
        
#         print(f"\n{'='*50}")
#         print(f"Request ID: {request_id}")
#         print(f"Raw input: {input_data.data}")
        
#         #  PREPROCESSING PIPELINE
#         df = preprocess_input(input_data.data)
        
#         # Predict
#         prediction = model.predict(df)[0]
        
#         print(f"Prediction: {prediction}")
#         print(f"{'='*50}\n")
        
#         # ---------------- LOGGING ---------------- #
#         log_entry = input_data.data.copy()
#         log_entry["prediction"] = prediction
#         log_entry["request_id"] = request_id
#         log_entry["timestamp"] = datetime.now()
        
#         log_df = pd.DataFrame([log_entry])
        
#         if os.path.exists(LOG_PATH):
#             log_df.to_csv(LOG_PATH, mode="a", header=False, index=False)
#         else:
#             log_df.to_csv(LOG_PATH, index=False)
        
#         return {
#             "request_id": request_id,
#             "prediction": prediction,
#             "status": "success"
#         }
    
#     except Exception as e:
#         print(f"ERROR: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/health")
# def health_check():
#     return {"status": "healthy", "model_loaded": model is not None}


import traceback
import os
import uuid
import joblib
import csv
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.utils.preprocessing import preprocess_input
app = FastAPI(title="Traffic Classification API")

# Use Environment Variable or default path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models", "tuned_model.pkl"))
model = joblib.load(MODEL_PATH)

class PredictionInput(BaseModel):
    data: dict

@app.post("/predict")
def predict(input_data: PredictionInput):
    try:

        request_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Preprocess using the selective pipeline
        processed_df = preprocess_input(input_data.data)
        
        # Predict
        prediction = model.predict(processed_df)[0]

        log_file = "src/prediction_logs.csv"
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            # Write header if file is new
            if not file_exists:
                writer.writerow(["timestamp", "request_id", "input_data", "prediction"])
            
            # Write the log row
            writer.writerow([timestamp, request_id, str(input_data.data), str(prediction)])
        return {
            "request_id": request_id,
            "prediction": str(prediction),
            "status": "success"
        }
    except Exception as e:
        print("ERROR DURING PREDICTION")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy"}