def fibonacci_first_n(n):
    """
    Return the first n Fibonacci numbers.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]
    seq = [0, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]

if __name__ == "__main__":
    result = fibonacci_first_n(10)
    print(result)
