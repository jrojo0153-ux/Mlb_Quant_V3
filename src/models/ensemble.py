import numpy as np

class EnsembleModel:

    def __init__(self, xgb, lgb, cat):

        self.xgb = xgb
        self.lgb = lgb
        self.cat = cat

    def predict_proba(self, X):

        p1 = self.xgb.predict_proba(X)[:,1]
        p2 = self.lgb.predict_proba(X)[:,1]
        p3 = self.cat.predict_proba(X)[:,1]

        return (0.4*p1 + 0.35*p2 + 0.25*p3)
