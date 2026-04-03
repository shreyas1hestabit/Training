def is_palindrome(num):
    num_str = str(num)
    return num_str == num_str[::-1]

def get_user_input():
    while True:
        try:
            num = int(input("Enter a number to check if it's a palindrome: "))
            return num
        except ValueError:
            print("Invalid input: Please enter a whole number")

def main():
    num = get_user_input()
    if is_palindrome(num):
        print("Is Palindrome: The number is a palindrome")
    else:
        print("Is Not Palindrome: The number is not a palindrome")

if __name__ == '__main__':
    main()
