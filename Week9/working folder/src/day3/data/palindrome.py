"""
Palindrome detection script.

This script provides a simple function `is_palindrome(s)` that checks if a given string is a palindrome.
It ignores case and non-alphanumeric characters.
The script also contains a small demo when run as a main program.
"""
import re

def is_palindrome(s: str) -> bool:
    """Return True if the given string is a palindrome.

    The function normalizes the string by removing non-alphanumeric characters
    and converting to lowercase before performing the palindrome check.
    """
    cleaned = re.sub(r"[^A-Za-z0-9]", "", s).lower()
    return cleaned == cleaned[::-1]

if __name__ == "__main__":
    examples = [
        "A man, a plan, a canal: Panama",
        "racecar",
        "hello",
        "Madam In Eden, I'm Adam",
    ]
    for text in examples:
        print(f"{text!r} -> {is_palindrome(text)}")
