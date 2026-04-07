def reverse_string(s):
    # Reverse the input string using slicing
    return s[::-1]

def main():
    # Hardcoded example values
    example_values = ["Hello World", "Python", "Programming", "Example"]

    # Iterate over each example value
    for value in example_values:
        reversed_value = reverse_string(value)
        print(f"Original String: {value}")
        print(f"Reversed String: {reversed_value}")
        print()

if __name__ == '__main__': 
    main()
