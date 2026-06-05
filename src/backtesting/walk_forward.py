import pandas as pd

def walk_forward_split(df, train_size=0.7):

    split = int(len(df)*train_size)

    train = df.iloc[:split]
    test = df.iloc[split:]

    return train, test
