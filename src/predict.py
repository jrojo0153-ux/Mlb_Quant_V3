import joblib

from src.config import MODEL_PATH

def predict(df):

    model = joblib.load(MODEL_PATH)

    probs = model.predict_proba(df)

    return probs[:,1]
