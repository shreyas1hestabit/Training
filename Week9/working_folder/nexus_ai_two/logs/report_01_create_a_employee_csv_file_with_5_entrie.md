# NEXUS AI Report

**Task:** create a employee.csv file with 5 entries each with name, phone, employee_ID, address

---

## Creating Employee CSV File

### Task: Create an "employee.csv" file with 5 entries each with "name", "phone", "employee_ID", and "address".

### Solution:

```python
# Import necessary libraries
import csv

# Define the data
data = [
    {"name": "John Doe", "phone": "123-456-7890", "employee_ID": "E001", "address": "123 Main St"},
    {"name": "Jane Smith", "phone": "098-765-4321", "employee_ID": "E002", "address": "456 Oak St"},
    {"name": "Bob Johnson", "phone": "111-222-3333", "employee_ID": "E003", "address": "789 Pine St"},
    {"name": "Alice Brown", "phone": "444-555-6666", "employee_ID": "E004", "address": "321 Maple St"},
    {"name": "Charlie Davis", "phone": "777-888-9999", "employee_ID": "E005", "address": "901 Cedar St"}
]

# Function to create a CSV file
def create_csv(data, filename):
    fieldnames = ["name", "phone", "employee_ID", "address"]
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Usage example
if __name__ == "__main__":
    filename = "employee.csv"
    create_csv(data, filename)
    print(f"CSV file {filename} created successfully.")
```

This code snippet creates an "employee.csv" file with 5 entries each with "name", "phone", "employee_ID", and "address" fields as per the original task. The output only includes the relevant code to accomplish the task and does not include any additional information from previous tasks or discussions.