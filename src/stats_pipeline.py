from pybaseball import team_batting, team_pitching
import pandas as pd

def get_team_stats(season=2024):

    batting = team_batting(season)
    pitching = team_pitching(season)

    batting = batting[["Team", "R", "OBP", "SLG", "OPS"]]
    pitching = pitching[["Team", "ERA", "WHIP", "SO9"]]

    return batting, pitching
