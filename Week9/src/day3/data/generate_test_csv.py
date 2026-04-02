import csv
import random
import string

num_rows = 1000

with open("test.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow(["id", "name", "value"])
    for i in range(1, num_rows + 1):
        # Generate random 5-letter name
        name = ''.join(random.choices(string.ascii_letters, k=5))
        value = random.randint(0, 1000)
        writer.writerow([i, name, value])

print("test.csv generated with", num_rows, "rows of random data.")
