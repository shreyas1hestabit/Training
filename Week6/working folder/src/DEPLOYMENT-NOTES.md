# Deployment Notes

## Run API
uvicorn deployment.api:app --reload

## Endpoint
POST /predict

## Features
- Input validation using Pydantic
- Prediction logging
- Model versioning

## Docker
docker build -t ml-api .
docker run -p 8000:8000 ml-api

## Monitoring
- Data drift using KS test
- Track predictions via logs

## Conclusion
Model ready for production deployment.
