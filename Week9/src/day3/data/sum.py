"""
sum.py
-------
This script demonstrates how to compute the sum of the first `n` natural numbers
using a simple mathematical formula.

The core function `sum_first_n(n)` returns the sum of the series
1 + 2 + 3 + ... + n.

Example usage:
    >>> sum_first_n(10)
    55

The `if __name__ == "__main__":` block provides a quick manual test.
"""

def sum_first_n(n: int) -> int:
    """Return the sum of the first ``n`` natural numbers.

    Args:
        n: An integer greater than or equal to 0.

    Returns:
        The arithmetic sum of numbers from 1 to ``n``.
    """
    if n < 0:
        raise ValueError("n must be non‑negative")
    return n * (n + 1) // 2

if __name__ == "__main__":
    # Simple test
    for test_n in [5, 10, 20]:
        print(f"Sum of first {test_n} natural numbers: {sum_first_n(test_n)}")
