"""Fibonacci series module"""

def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number.

    Parameters
    ----------
    n : int
        Position in the Fibonacci sequence (0-indexed).

    Returns
    -------
    int
        nth Fibonacci number.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python fib.py <n>")
        sys.exit(1)
    n = int(sys.argv[1])
    print(fibonacci(n))
