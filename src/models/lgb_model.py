import lightgbm as lgb
import joblib

def train_lgb(X_train, y_train):

    model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.03,
        num_leaves=31
    )

    model.fit(X_train, y_train)

    joblib.dump(model, "models/lgb.pkl")

    return model
