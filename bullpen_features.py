import pandas as pd

class BullpenFeatures:

    def __init__(self, bullpen_df):
        self.df = bullpen_df.copy()

    def calculate_fatigue(self):

        self.df["fatigue_score"] = (
            self.df["innings_last_3_days"] * 0.5
            + self.df["innings_last_7_days"] * 0.3
            + self.df["relievers_used_last_3_days"] * 0.2
        )

        return self.df
