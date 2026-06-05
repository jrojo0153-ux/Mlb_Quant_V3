from sklearn.isotonic import IsotonicRegression

class Calibrator:

    def __init__(self):

        self.iso = IsotonicRegression(out_of_bounds="clip")

    def fit(self, preds, y):

        self.iso.fit(preds, y)

    def predict(self, preds):

        return self.iso.transform(preds)
