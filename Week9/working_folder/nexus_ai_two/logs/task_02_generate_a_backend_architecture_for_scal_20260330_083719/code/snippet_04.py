# Usage example
from flask import Flask, jsonify, request

# Create a Flask application instance
app = Flask(__name__)

# Create a client to send a request to the /analyze endpoint
import requests

# Send a GET request to the /analyze endpoint
response = requests.get('http://localhost:5000/analyze')

# Print the response
print(response.json())