import pandas as pd
import joblib

from xgboost import XGBClassifier

from src.config import MODEL_PATH

def train(df):

    X = df.drop("target",axis=1)

    y = df["target"]

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05
    )

    model.fit(X,y)

    joblib.dump(model,MODEL_PATH)

    return model
