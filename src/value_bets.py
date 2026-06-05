import pandas as pd

def calculate_ev(df):

    df["market_prob"] = 1 / df["odds"]

    df["edge"] = df["model_prob"] - df["market_prob"]

    df["ev"] = (df["model_prob"] * df["odds"]) - 1

    return df
