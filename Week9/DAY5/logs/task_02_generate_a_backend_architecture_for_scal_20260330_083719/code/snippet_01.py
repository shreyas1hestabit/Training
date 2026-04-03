# Import required libraries
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Create a Flask application instance
app = Flask(__name__)

# Configure the application to use a SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy and Marshmallow extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Define a User model
class User(db.Model):
    # Define the table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    # Create a representation of the User model
    def __init__(self, name, email):
        self.name = name
        self.email = email

# Create a schema for the User model
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

# Create a route to handle GET requests
@app.route('/users', methods=['GET'])
def get_users():
    # Query the database for all users
    users = User.query.all()
    # Create a schema instance
    user_schema = UserSchema(many=True)
    # Serialize the users data
    users_data = user_schema.dump(users)
    # Return the serialized data as JSON
    return jsonify(users_data)

# Create a route to handle POST requests
@app.route('/users', methods=['POST'])
def create_user():
    # Get the request data
    data = request.get_json()
    # Create a new User instance
    new_user = User(data['name'], data['email'])
    # Add the new user to the database session
    db.session.add(new_user)
    # Commit the changes to the database
    db.session.commit()
    # Return a success message
    return jsonify({'message': 'User created successfully'}), 201

# Create the database tables
with app.app_context():
    db.create_all()

# Run the application
if __name__ == '__main__':
    # Run the application on port 5000
    app.run(port=5000)