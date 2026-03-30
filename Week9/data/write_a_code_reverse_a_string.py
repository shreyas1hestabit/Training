def reverse_string(input_str):
    # Reverse the input string
    return input_str[::-1]

def main():
    # Get user input
    user_input = input("Enter a string to reverse: ")
    
    # Reverse the input string
    reversed_str = reverse_string(user_input)
    
    # Print the result
    print("Reversed String:", reversed_str)

if __name__ == '__main__': 
    main()
