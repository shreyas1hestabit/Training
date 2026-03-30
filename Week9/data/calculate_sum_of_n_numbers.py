# Function to calculate the sum of n numbers
def calculate_sum():
    # Get the value of n from the user
    while True:
        try:
            n = int(input("Enter the number of values to sum: "))
            break
        except ValueError:
            print("Invalid input: Please enter a whole number")

    # Initialize sum to 0
    total = 0

    # Get n numbers from the user and calculate the sum
    for i in range(n):
        while True:
            try:
                num = float(input(f"Enter number {i+1}: "))
                total += num
                break
            except ValueError:
                print("Invalid input: Please enter a number")

    return total

# Main function
def main():
    print("Sum of n Numbers Calculator")
    print("---------------------------")
    sum_of_numbers = calculate_sum()
    print(f"Sum of the numbers: {sum_of_numbers}")

if __name__ == '__main__':
    main()
