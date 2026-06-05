
import logging
import joblib
import pandas as pd
import asyncio
import os
from telegram import Bot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('bot_mlb_prod.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def notify_telegram(msg):
    # Prioridad: Secret de GitHub Environment -> Valor por defecto
    TOKEN = os.getenv('TELEGRAM_TOKEN', '8766709924:AAGOgVeUB39ZsH7b5BDWxvXvQCapmpiqbAo')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '8536626773')
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
        logger.info("Notificación enviada con éxito.")
    except Exception as e:
        logger.error(f'Error en Telegram: {e}')

class MLBKaggleBot:
    def __init__(self):
        self.models = {
            'xgb': joblib.load('models/xgb_model.pkl'),
            'lgb': joblib.load('models/lgb_model.pkl'),
            'cat': joblib.load('models/cat_model.pkl')
        }

    async def run_inference(self):
        if not os.path.exists('game_logs.csv'):
            logger.error("Dataset no encontrado.")
            return

        df = pd.read_csv('game_logs.csv', low_memory=False).tail(10)
        cols = ['h_score', 'v_score', 'h_walks', 'v_walks', 'h_errors', 'v_errors']
        X = df[cols].fillna(0)

        # Ensamble
        p1 = self.models['xgb'].predict_proba(X)[:, 1]
        p2 = self.models['lgb'].predict_proba(X)[:, 1]
        p3 = self.models['cat'].predict_proba(X)[:, 1]
        probs = (p1 + p2 + p3) / 3

        report = "⚾️ *MLB Quant V3: Live Report* ⚾️\n\n"
        for i, prob in enumerate(probs):
            report += f"🔹 *Juego {i+1}*: Prob. Victoria Local: `{prob:.2%}`\n"
        
        await notify_telegram(report)

if __name__ == '__main__':
    bot = MLBKaggleBot()
    asyncio.run(bot.run_inference())
