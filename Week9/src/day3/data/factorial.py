"""
Factorial calculation script.
Usage:
    python factorial.py 5

This will calculate 5! and print the result.
"""

import sys


def factorial(n: int) -> int:
    """Return the factorial of a non‑negative integer n.

    Raises
    ------
    ValueError
        If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python factorial.py <non‑negative integer>")
        sys.exit(1)
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Please provide an integer.")
        sys.exit(1)
    try:
        print(factorial(n))
    except ValueError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
