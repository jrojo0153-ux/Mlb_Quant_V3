import json
from typing import Dict, List
from src.feature_engineering import FeatureEngineer
from src.probability_calculator import ProbabilityCalculator
from src.data_fetcher import MLBDataFetcher
import logging

logger = logging.getLogger(__name__)

class AnalysisEngine:
    """
    Motor de análisis predictivo para mercados MLB
    Calcula las 5 opciones de mayor probabilidad de cumplimiento
    """
    
    def __init__(self, odds_api_key):
        self.fetcher = MLBDataFetcher(odds_api_key)
        self.fe = FeatureEngineer()
        self.pc = ProbabilityCalculator(self.fe, self.fetcher)
    
    def analyze_game(self, home_team: str, away_team: str, park_name: str) -> Dict:
        """
        Análisis completo de un partido MLB
        Retorna 5 mercados con máxima probabilidad de cumplimiento
        """
        
        # Obtener datos necesarios
        home_pitcher = self.fetcher.get_pitcher_stats(home_team)
        away_pitcher = self.fetcher.get_pitcher_stats(away_team)
        
        home_batter = self.fetcher.get_batter_stats(home_team[:3].upper())
        away_batter = self.fetcher.get_batter_stats(away_team[:3].upper())
        
        weather = self.fetcher.get_weather(park_name, None)
        home_bullpen = self.fetcher.get_bullpen_metrics(home_team[:3].upper())
        away_bullpen = self.fetcher.get_bullpen_metrics(away_team[:3].upper())
        
        park_factors = self.fe.park_factors.get(park_name, {"run_factor": 1.0, "hr_factor": 1.0})
        
        # Calcular probabilidades para cada mercado
        markets_analysis = []
        
        # 1. NRFI - No Runs First Inning
        nrfi_prob, nrfi_details = self.pc.calculate_nrfi_probability(
            home_pitcher, away_pitcher, home_batter, away_batter
        )
        markets_analysis.append({
            'market': 'NRFI (No Runs First Inning)',
            'probability': nrfi_prob,
            'market_line': '-130',
            'key_features': {
                'home_so_rate': nrfi_details['home_strikeout_rate'],
                'away_so_rate': nrfi_details['away_strikeout_rate'],
                'home_pitcher_k%': home_pitcher['K_percent'],
                'away_pitcher_k%': away_pitcher['K_percent']
            },
            'volatility': 'Bajo (primera entrada predecible con K-rates altos)'
        })
        
        # 2. Primeras 5 Entradas ML - Home
        first5_home_prob, first5_details = self.pc.calculate_first_5_ml(
            home_pitcher, away_pitcher, home_batter, away_batter, park_name, weather
        )
        markets_analysis.append({
            'market': f'Primeras 5 Entradas - {home_team.upper()}',
            'probability': first5_home_prob,
            'market_line': '-110',
            'key_features': {
                'home_pitcher_fip': home_pitcher['FIP'],
                'away_pitcher_fip': away_pitcher['FIP'],
                'home_wrc_plus': home_batter['wRC_plus'],
                'weather_multiplier': first5_details['weather_multiplier'],
                'first_inning_advantage': 1.05
            },
            'volatility': 'Moderado (climatología y fatiga del bullpen en juego tardío)'
        })
        
        # 3. Primeras 5 Entradas ML - Away
        first5_away_prob = 1 - first5_home_prob
        markets_analysis.append({
            'market': f'Primeras 5 Entradas - {away_team.upper()}',
            'probability': first5_away_prob,
            'market_line': '-110',
            'key_features': {
                'away_pitcher_fip': away_pitcher['FIP'],
                'home_pitcher_fip': home_pitcher['FIP'],
                'away_wrc_plus': away_batter['wRC_plus'],
                'away_on_road': True
            },
            'volatility': 'Moderado-Alto (desventaja local adicional)'
        })
        
        # 4. Team Total Under - Home
        _, under_details_home = self.pc.calculate_team_total_under(
            away_pitcher, home_batter, 4.0, park_factors['run_factor']
        )
        home_under_prob = 1 - (under_details_home['expected_runs'] / 8.0)  # Normalizar
        markets_analysis.append({
            'market': f'Team Total Under {home_team.upper()} 4.5',
            'probability': max(0.35, min(0.70, home_under_prob)),
            'market_line': '4.5 (-110)',
            'key_features': {
                'away_pitcher_era': away_pitcher['ERA'],
                'away_pitcher_xfip': away_pitcher['xFIP'],
                'home_team_wrc_plus': home_batter['wRC_plus'],
                'expected_runs': under_details_home['expected_runs'],
                'bullpen_reliability': self.fe.bullpen_reliability(home_bullpen)
            },
            'volatility': 'Moderado (dependiente del desempeño del bullpen en entrada 6-9)'
        })
        
        # 5. Game Total Over
        over_prob, over_details = self.pc.calculate_over_under_game(
            home_pitcher, away_pitcher, home_batter, away_batter, 8.5, park_factors
        )
        markets_analysis.append({
            'market': 'Game Total Over 8.5',
            'probability': over_prob,
            'market_line': '8.5 (-110)',
            'key_features': {
                'home_exp_runs': over_details['home_expected_runs'],
                'away_exp_runs': over_details['away_expected_runs'],
                'total_expected': over_details['total_expected'],
                'park_run_factor': park_factors['run_factor'],
                'weather_temp': weather['temperature_f']
            },
            'volatility': 'Alto (bullpen fatiga y varianza de BABIP en innings tardías)'
        })
        
        # Ordenar por probabilidad descendente
        markets_analysis.sort(key=lambda x: x['probability'], reverse=True)
        
        return {
            'matchup': f"{away_team} @ {home_team}",
            'park': park_name,
            'weather': weather,
            'top_5_markets': markets_analysis[:5]
        }
    
    def generate_json_report(self, game_analysis: Dict) -> str:
        """
        Genera reporte JSON estructurado con las 5 opciones analizadas
        """
        report = {
            'matchup': game_analysis['matchup'],
            'generated_at': '2026-06-05',
            'opciones_clasificadas': []
        }
        
        for idx, market in enumerate(game_analysis['top_5_markets'], 1):
            option_data = {
                "opcion_clasificada": {
                    "ranking_probabilidad": str(idx),
                    "mercado_mlb": market['market'],
                    "linea_propuesta": market['market_line'],
                    "probabilidad_matematica_estimada": f"{market['probability']*100:.1f}%",
                    "score_de_confianza_modelo": f"{min(0.95, market['probability'])*0.95:.2f}",
                    "variables_clave_explicativas": market['key_features'],
                    "analisis_de_volatilidad": market['volatility']
                }
            }
            report['opciones_clasificadas'].append(option_data)
        
        return json.dumps(report, indent=2, ensure_ascii=False)
