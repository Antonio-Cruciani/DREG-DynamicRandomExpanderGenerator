import random as rnd
# Function that return the binomial coefficient (n over k)
def get_binomial(n, k):
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0



# Function for biased coin toss
def flip(p):
    return 'H' if rnd.random() < p else 'T'

