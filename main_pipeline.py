
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
    logger.info("Ejecutando Pipeline V5 (Corrección de enfrentamientos)...")
    
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
            
            # Probabilidad base (Placeholder)
            win_prob = 0.54 
            
            match_odds = next((m for m in market_odds if home_team in m['home_team']), None)
            odds_display = "N/A"
            ev = -1
            
            if match_odds:
                bookie = match_odds['bookmakers'][0]
                odds = next(o['price'] for o in bookie['markets'][0]['outcomes'] if o['name'] == match_odds['home_team'])
                ev = (win_prob * odds) - 1
                odds_display = f"{odds}"

            # Formato corregido: Visitante @ Local
            matchup_line = f"⚾️ *{away_team}* @ *{home_team}*"
            stats_line = f"Prob: `{win_prob:.1%}` | Odds: `{odds_display}`"
            
            if ev > 0:
                value_bets.append(f"{matchup_line}\n   {stats_line}\n   🚀 *EV: {ev:+.2%}*")
            else:
                ev_label = f"{ev:+.2%}" if ev != -1 else "N/A"
                other_games.append(f"{matchup_line}\n   {stats_line}\n   EV: `{ev_label}`")
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
        logger.info("Reporte corregido enviado.")

if __name__ == '__main__':
    asyncio.run(run_pro_pipeline())
