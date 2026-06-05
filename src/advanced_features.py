import pandas as pd

def build_features(games, batting, pitching):

    df = games.copy()

    # Merge simple inicial (fase 1.1)
    df = df.merge(batting, left_on="home", right_on="Team", how="left")
    df = df.merge(pitching, left_on="home", right_on="Team", how="left", suffixes=("_bat_home","_pit_home"))

    df = df.merge(batting, left_on="away", right_on="Team", how="left")
    df = df.merge(pitching, left_on="away", right_on="Team", how="left", suffixes=("_bat_away","_pit_away"))

    # Features básicas

    df["offense_gap"] = df["OPS_bat_home"] - df["OPS_bat_away"]
    df["pitching_gap"] = df["ERA_pit_away"] - df["ERA_pit_home"]

    df["home_advantage"] = 1

    return df
