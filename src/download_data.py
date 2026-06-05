import requests
import pandas as pd

def get_schedule(date):

    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"

    r = requests.get(url)

    data = r.json()

    games = []

    for d in data.get("dates",[]):

        for game in d.get("games",[]):

            games.append({
                "gamePk": game["gamePk"],
                "home": game["teams"]["home"]["team"]["name"],
                "away": game["teams"]["away"]["team"]["name"]
            })

    return pd.DataFrame(games)
