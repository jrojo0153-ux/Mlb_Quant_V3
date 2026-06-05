def kelly_fraction(prob, odds):

    b = odds - 1
    q = 1 - prob

    f = (b*prob - q) / b

    return max(0, f)
