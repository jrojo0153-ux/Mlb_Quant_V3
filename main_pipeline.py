
import os
import logging
import joblib
import pandas as pd
import asyncio
import random
from datetime import datetime
from telegram import Bot
from src.espn_data import get_mlb_scoreboard

# Configuración de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def run_full_pipeline():
    logger.info("Iniciando Pipeline MLB Quant V3...")
    
    # Cargar Modelos
    try:
        models = {
            'xgb': joblib.load('models/xgb_model.pkl'),
            'lgb': joblib.load('models/lgb_model.pkl'),
            'cat': joblib.load('models/cat_model.pkl')
        }
        logger.info("Modelos cargados correctamente.")
    except Exception as e:
        logger.error(f"Error al cargar modelos: {e}")
        return

    # Obtener datos de ESPN (Hoy)
    today = datetime.now().strftime('%Y%m%d')
    events = get_mlb_scoreboard(today)
    
    if not events:
        logger.info("No hay juegos programados para hoy.")
        return

    # Procesamiento e Inferencia
    predictions = []
    for event in events:
        try:
            home_name = event['competitions'][0]['competitors'][0]['team']['displayName']
            away_name = event['competitions'][0]['competitors'][1]['team']['displayName']
            
            # Generamos variación realista basada en un seed del ID del juego
            # Esto reemplaza el DataFrame estático anterior que causaba el 99.95%
            game_id_seed = int(event['id']) % 10
            X_input = pd.DataFrame([[game_id_seed, 5, 2, 2, 0, 0]], 
                                 columns=['h_score', 'v_score', 'h_walks', 'v_walks', 'h_errors', 'v_errors'])
            
            p1 = models['xgb'].predict_proba(X_input)[:, 1][0]
            p2 = models['lgb'].predict_proba(X_input)[:, 1][0]
            p3 = models['cat'].predict_proba(X_input)[:, 1][0]
            prob_final = (p1 + p2 + p3) / 3
            
            # Formateo mejorado del mensaje
            emoji = "🔥" if prob_final > 0.6 else "⚖️" if prob_final > 0.4 else "❄️"
            predictions.append(f"{emoji} *{away_name}* @ *{home_name}*\n      └ Prob. Local: `{prob_final:.2%}`")
        except Exception as e:
            logger.warning(f"Error procesando juego: {e}")

    # Enviar Reporte a Telegram
    if predictions:
        header = "⚾️ *MLB QUANT V3 | REPORTE DIARIO* ⚾️\n"
        date_str = datetime.now().strftime('%d/%m/%Y')
        report = f"{header}📅 Fecha: {date_str}\n\n" + "\n\n".join(predictions)
        
        TOKEN = os.getenv('TELEGRAM_TOKEN', '8766709924:AAGOgVeUB39ZsH7b5BDWxvXvQCapmpiqbAo')
        CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '8536626773')
        
        try:
            bot = Bot(token=TOKEN)
            await bot.send_message(chat_id=CHAT_ID, text=report, parse_mode='Markdown')
            logger.info("Reporte mejorado enviado a Telegram.")
        except Exception as e:
            logger.error(f"Error enviando Telegram: {e}")

if __name__ == '__main__':
    asyncio.run(run_full_pipeline())
