from src.historical_data import get_season_games
from src.stats_pipeline import get_team_stats
from src.advanced_features import build_features
from src.label_builder import create_target

import pandas as pd

def build_dataset():

    games = get_season_games("2023-03-30","2024-10-30")

    batting, pitching = get_team_stats(2024)

    df = build_features(games, batting, pitching)

    df = create_target(df)

    df = df.dropna()

    df.to_csv("data/training_dataset.csv", index=False)

    return df
