import requests
import pandas as pd
from datetime import datetime, timedelta

BASE = "https://statsapi.mlb.com/api/v1/schedule"

def get_season_games(start_date="2023-03-30", end_date="2024-10-30"):

    all_games = []
    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    while current <= end:

        date_str = current.strftime("%Y-%m-%d")

        url = f"{BASE}?sportId=1&date={date_str}"
        r = requests.get(url).json()

        for d in r.get("dates", []):
            for g in d.get("games", []):

                all_games.append({
                    "gamePk": g["gamePk"],
                    "date": date_str,
                    "home": g["teams"]["home"]["team"]["name"],
                    "away": g["teams"]["away"]["team"]["name"],
                    "home_score": g["teams"]["home"].get("score", 0),
                    "away_score": g["teams"]["away"].get("score", 0),
                    "home_win": int(g["teams"]["home"].get("score",0) > g["teams"]["away"].get("score",0))
                })

        current += timedelta(days=1)

    return pd.DataFrame(all_games)
