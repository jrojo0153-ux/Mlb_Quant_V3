import numpy as np

def roi(profits):

    return np.sum(profits) / len(profits)

def accuracy(preds, y):

    return (preds == y).mean()
