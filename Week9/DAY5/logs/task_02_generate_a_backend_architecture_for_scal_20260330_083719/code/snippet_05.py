# Import required libraries
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import redis

# Create a Flask application instance
app = Flask(__name__)

# Configure the application to use a SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy and Marshmallow extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Create a Redis client instance
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Define a function to cache data
def cache_data(key, data):
    redis_client.set(key, data)

# Define a function to retrieve cached data
def get_cached_data(key):
    return redis_client.get(key)

# Example usage:
@app.route('/data', methods=['GET'])
def get_data():
    key = 'data'
    cached_data = get_cached_data(key)
    if cached_data:
        return jsonify({'data': cached_data})
    else:
        data = {'key': 'value'}  # Replace with actual data retrieval
        cache_data(key, data)
        return jsonify({'data': data})