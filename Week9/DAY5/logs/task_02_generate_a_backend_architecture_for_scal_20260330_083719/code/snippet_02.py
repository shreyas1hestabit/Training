# Example usage:
import requests

# Create a new user
new_user = {
    'name': 'John Doe',
    'email': 'johndoe@example.com'
}

response = requests.post('http://localhost:5000/users', json=new_user)

# Print the response
print(response.json())

# Get all users
response = requests.get('http://localhost:5000/users')

# Print the response
print(response.json())