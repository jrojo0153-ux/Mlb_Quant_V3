import pandas as pd

class PitcherFeatures:

    @staticmethod
    def pitcher_rating(df):

        df["pitcher_rating"] = (
            (-2.0 * df["ERA"])
            + (-1.5 * df["FIP"])
            + (0.08 * df["K_percent"])
            - (0.05 * df["BB_percent"])
            - (0.40 * df["WHIP"])
        )

        return df
