
import requests
import pandas as pd

def get_mlb_scoreboard(date_str):
    url = f'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={date_str}'
    r = requests.get(url)
    events = r.json().get('events', [])
    return events
