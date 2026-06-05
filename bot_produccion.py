
import logging
import joblib
import pandas as pd
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('bot_mlb_prod.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class MLBKaggleBot:
    def __init__(self, kelly_fraction=0.02):
        try:
            self.xgb = joblib.load('models/xgb_model.pkl')
            self.lgb = joblib.load('models/lgb_model.pkl')
            self.cat = joblib.load('models/cat_model.pkl')
            logger.info('Ensamble cargado desde modelos de Kaggle.')
        except Exception as e:
            logger.error(f'Error cargando modelos: {e}')

        self.bankroll = 1000.0
        self.kelly_fraction = kelly_fraction

    def run_inference(self):
        logger.info('Iniciando inferencia sobre dataset histórico...')
        try:
            df = pd.read_csv('game_logs.csv', low_memory=False).tail(10)
            features = df[['h_score', 'v_score', 'h_walks', 'v_walks', 'h_errors', 'v_errors']].fillna(0)

            p1 = self.xgb.predict_proba(features)[:, 1]
            p2 = self.lgb.predict_proba(features)[:, 1]
            p3 = self.cat.predict_proba(features)[:, 1]

            final_probs = (p1 + p2 + p3) / 3

            for i, prob in enumerate(final_probs):
                logger.info(f'[INFO] Juego Histórico {i}: Probabilidad Local {prob:.2%}')
        except Exception as e:
            logger.error(f'Error en ciclo: {e}')

if __name__ == "__main__":
    bot = MLBKaggleBot()
    bot.run_inference()
