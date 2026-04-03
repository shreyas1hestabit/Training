import math

def calculate_factorial(n):
    # Calculate the factorial of a number using math library
    try:
        factorial = math.factorial(n)
        return factorial
    except ValueError:
        return None

def main():
    print("Factorial Calculator Program")
    print("-------------------------------")
    
    # Get user input for the number
    while True:
        try:
            num = int(input("Enter a non-negative integer: "))
            if num < 0:
                print("Error: Factorial is not defined for negative numbers")
                continue
            break
        except ValueError:
            print("Error: Invalid input. Please enter a valid integer.")
            
    # Calculate and print the factorial
    factorial = calculate_factorial(num)
    if factorial is not None:
        print("Factorial Result:", factorial)
    else:
        print("Error: Unable to calculate factorial")

if __name__ == '__main__': 
    main()
