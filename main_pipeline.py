
import os
import logging
import requests
import joblib
import pandas as pd
import asyncio
from datetime import datetime
from telegram import Bot
from src.espn_data import get_mlb_scoreboard

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

ODDS_API_KEY = os.getenv('ODDS_API_KEY', '3bb02dc2c1b752b85d21e2503b4323cb')

def get_live_odds():
    url = f'https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API_KEY}&regions=us&markets=h2h&oddsFormat=decimal'
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

async def run_pro_pipeline():
    logger.info("Ejecutando Pipeline V5 (Inclusión de Recomendación de Equipo)...")

    try:
        models = {'xgb': joblib.load('models/xgb_model.pkl'), 'lgb': joblib.load('models/lgb_model.pkl'), 'cat': joblib.load('models/cat_model.pkl')}
    except:
        logger.error("Modelos no encontrados.")
        return

    market_odds = get_live_odds()
    events = get_mlb_scoreboard(datetime.now().strftime('%Y%m%d'))

    value_bets = []
    other_games = []

    for event in events:
        try:
            home_team = event['competitions'][0]['competitors'][0]['team']['displayName']
            away_team = event['competitions'][0]['competitors'][1]['team']['displayName']

            # Probabilidad base de victoria Local (Home Win)
            win_prob_home = 0.54
            
            match_odds = next((m for m in market_odds if home_team in m['home_team']), None)
            if not match_odds: continue

            bookie = match_odds['bookmakers'][0]
            # Obtener cuotas para Home y Away
            odds_home = next(o['price'] for o in bookie['markets'][0]['outcomes'] if o['name'] == match_odds['home_team'])
            odds_away = next(o['price'] for o in bookie['markets'][0]['outcomes'] if o['name'] == match_odds['away_team'])

            # Calcular EV para Home
            ev_home = (win_prob_home * odds_home) - 1
            # Calcular EV para Away (usando probabilidad inversa)
            ev_away = ((1 - win_prob_home) * odds_away) - 1

            matchup_line = f"⚾️ *{away_team}* @ *{home_team}*"
            
            if ev_home > 0:
                value_bets.append(f"{matchup_line}\n   ✅ *Pick: {home_team}*\n   Prob: `{win_prob_home:.1%}` | Odds: `{odds_home}` | 🚀 *EV: {ev_home:+.2%}*")
            elif ev_away > 0:
                value_bets.append(f"{matchup_line}\n   ✅ *Pick: {away_team}*\n   Prob: `{1-win_prob_home:.1%}` | Odds: `{odds_away}` | 🚀 *EV: {ev_away:+.2%}*")
            else:
                ev_display = ev_home if ev_home > ev_away else ev_away
                team_display = home_team if ev_home > ev_away else away_team
                other_games.append(f"{matchup_line}\n   EV Máx: `{ev_display:+.2%}` ({team_display})\n   Status: `Sin Valor`")
        except Exception as e:
            continue

    report = "📊 *MLB QUANT V5 | MASTER REPORT* 📊\n\n"
    if value_bets:
        report += "🎯 *APUESTAS CON VALOR (EV+)*\n" + "\n".join(value_bets) + "\n\n"
    if other_games:
        report += "⚖️ *RESTO DE LA JORNADA*\n" + "\n".join(other_games)

    if value_bets or other_games:
        TOKEN = os.getenv('TELEGRAM_TOKEN', '8766709924:AAGOgVeUB39ZsH7b5BDWxvXvQCapmpiqbAo')
        CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '8536626773')
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=report, parse_mode='Markdown')
        logger.info("Reporte de apuestas enviado.")

if __name__ == '__main__':
    asyncio.run(run_pro_pipeline())
