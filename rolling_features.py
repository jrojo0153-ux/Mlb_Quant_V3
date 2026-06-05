import pandas as pd

class RollingFeatures:

    def __init__(self, games_df):
        self.games = games_df.copy()

    def add_team_rolling_stats(self):

        windows = [5, 10, 20]

        for window in windows:

            self.games[f"runs_scored_last_{window}"] = (
                self.games.groupby("team")["runs_scored"]
                .transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                )
            )

            self.games[f"runs_allowed_last_{window}"] = (
                self.games.groupby("team")["runs_allowed"]
                .transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                )
            )

            self.games[f"wins_last_{window}"] = (
                self.games.groupby("team")["win"]
                .transform(
                    lambda x: x.shift(1).rolling(window, min_periods=1).mean()
                )
            )

        return self.games
