
import pandas as pd
from pybaseball import pitching_stats, team_batting
from datetime import datetime

def get_advanced_metrics():
    # Obtener estadísticas de pitcheo del año actual
    current_year = datetime.now().year
    p_stats = pitching_stats(current_year)
    # Obtener home runs y métricas de bateo
    b_stats = team_batting(current_year)
    
    return p_stats, b_stats

def calculate_expected_value(win_prob, decimal_odds):
    # EV = (Probabilidad * Cuota) - 1
    ev = (win_prob * decimal_odds) - 1
    return ev
