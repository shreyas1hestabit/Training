#!/usr/bin/env python3
import csv
import random
import string


def random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def main():
    filename = 'sample.csv'
    fieldnames = ['id', 'name', 'value']
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(1, 1001):
            writer.writerow({
                'id': i,
                'name': random_name(),
                'value': random.randint(1, 1000)
            })


if __name__ == '__main__':
    main()
