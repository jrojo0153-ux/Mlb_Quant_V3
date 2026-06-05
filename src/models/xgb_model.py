import xgboost as xgb
import joblib

def train_xgb(X_train, y_train):

    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss"
    )

    model.fit(X_train, y_train)

    joblib.dump(model, "models/xgb.pkl")

    return model
