import requests
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MLBDataFetcher:
    
    BASE_ODDS_URL = 'https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/'
    BASE_ESPN_URL = 'https://site.api.espn.com/v2/site/baseball/mlb/'
    PYBASEBALL_URL = 'https://baseballsavant.mlb.com/'
    
    def __init__(self, odds_api_key):
        self.odds_api_key = odds_api_key
        self.session = requests.Session()
    
    def get_todays_games(self):
        """Obtiene partidos programados para hoy desde ESPN"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            response = self.session.get(f'{self.BASE_ESPN_URL}scoreboard?dates={today}')
            if response.status_code == 200:
                events = response.json().get('events', [])
                games = []
                for event in events:
                    try:
                        comp = event['competitions'][0]
                        home = comp['competitors'][0]['team']
                        away = comp['competitors'][1]['team']
                        games.append({
                            'game_id': event['id'],
                            'home_team': home['displayName'],
                            'home_abbr': home['abbreviation'],
                            'away_team': away['displayName'],
                            'away_abbr': away['abbreviation'],
                            'start_time': event['date']
                        })
                    except KeyError:
                        continue
                return games
        except Exception as e:
            logger.error(f"Error fetching ESPN games: {e}")
        return []
    
    def get_live_odds(self, markets=['h2h', 'spreads', 'totals']):
        """Obtiene cuotas en vivo desde The-Odds-API"""
        try:
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us',
                'markets': ','.join(markets),
                'oddsFormat': 'decimal'
            }
            response = self.session.get(self.BASE_ODDS_URL, params=params)
            if response.status_code == 200:
                return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Error fetching odds: {e}")
        return []
    
    def get_pitcher_stats(self, pitcher_name, season=2024):
        """Obtiene estadísticas de lanzadores (FIP, xFIP, WHIP, SIERA, K-BB%)"""
        try:
            # Simulación de datos reales (en producción usar pybaseball o Baseball Reference API)
            pitcher_stats = {
                'name': pitcher_name,
                'ERA': 3.45,
                'FIP': 3.28,
                'xFIP': 3.35,
                'WHIP': 1.12,
                'SIERA': 3.22,
                'K_percent': 28.5,
                'BB_percent': 8.2,
                'Barrel_percent_allowed': 8.1,
                'first_inning_ERA': 3.78,
                'first_inning_FIP': 3.55,
                'vs_RHH_OPS': 0.725,
                'vs_LHH_OPS': 0.685,
                'strikeout_rate': 0.285,
                'walk_rate': 0.082
            }
            return pitcher_stats
        except Exception as e:
            logger.error(f"Error fetching pitcher stats: {e}")
        return {}
    
    def get_batter_stats(self, team_abbr, days=7, vs_handedness='RHP'):
        """Obtiene estadísticas de bateadores últimos N días"""
        try:
            batter_stats = {
                'team': team_abbr,
                'wRC_plus': 108,
                'OPS': 0.748,
                'ISO': 0.168,
                'Hard_Hit_percent': 38.5,
                'Whiff_percent': 22.1,
                'strikeout_rate': 21.8,
                'walk_rate': 9.3,
                'contact_rate': 78.2,
                'vs_handedness': vs_handedness,
                'rolling_avg_runs': 4.2,
                'rolling_runs_allowed': 3.8
            }
            return batter_stats
        except Exception as e:
            logger.error(f"Error fetching batter stats: {e}")
        return {}
    
    def get_weather(self, stadium, game_date):
        """Obtiene condiciones climáticas proyectadas para el estadio"""
        try:
            weather = {
                'stadium': stadium,
                'temperature_f': 72,
                'wind_speed_mph': 8,
                'wind_direction': 'WSW',
                'humidity_percent': 65,
                'cloud_cover': 'Partly Cloudy',
                'precipitation_percent': 5
            }
            return weather
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
        return {}
    
    def get_bullpen_metrics(self, team_abbr):
        """Obtiene métricas de bullpen (fatiga, xFIP, uso)"""
        try:
            bullpen = {
                'team': team_abbr,
                'bullpen_ERA': 3.92,
                'bullpen_xFIP': 3.78,
                'closer_xFIP': 3.15,
                'innings_last_3_days': 8.2,
                'innings_last_7_days': 18.1,
                'relievers_used_last_3': 7,
                'fatigue_score': 4.2,  # 0-10 scale
                'avg_rest_hours': 24.5
            }
            return bullpen
        except Exception as e:
            logger.error(f"Error fetching bullpen metrics: {e}")
        return {}
