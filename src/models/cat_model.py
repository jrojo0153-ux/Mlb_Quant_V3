from catboost import CatBoostClassifier
import joblib

def train_cat(X_train, y_train):

    model = CatBoostClassifier(
        iterations=500,
        depth=6,
        learning_rate=0.03,
        verbose=False
    )

    model.fit(X_train, y_train)

    joblib.dump(model, "models/cat.pkl")

    return model
