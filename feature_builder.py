import pandas as pd

class FeatureBuilder:

    def build_matchup_features(
        self,
        home_team,
        away_team,
        home_pitcher,
        away_pitcher
    ):

        features = {}

        features["pitcher_edge"] = (
            home_pitcher["pitcher_rating"]
            - away_pitcher["pitcher_rating"]
        )

        features["offense_edge"] = (
            home_team["ops_last_20"]
            - away_team["ops_last_20"]
        )

        features["bullpen_edge"] = (
            away_team["bullpen_fatigue"]
            - home_team["bullpen_fatigue"]
        )

        features["home_field"] = 1

        return pd.DataFrame([features])
