import pandas as pd

def create_features(df):

    features = df.copy()

    features["home_field"] = 1

    return features
