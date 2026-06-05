import os
import json
import logging
from datetime import datetime
from src.analysis_engine import AnalysisEngine
from src.data_fetcher import MLBDataFetcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class ProductionPipeline:
    """
    Pipeline de producción para análisis predictivo MLB Quant V3
    Ejecuta análisis diarios completos y genera reportes en JSON
    """
    
    def __init__(self):
        self.odds_api_key = os.getenv('ODDS_API_KEY', '3bb02dc2c1b752b85d21e2503b4323cb')
        self.fetcher = MLBDataFetcher(self.odds_api_key)
        self.engine = AnalysisEngine(self.odds_api_key)
    
    def run_daily_analysis(self):
        """
        Ejecuta análisis completo para todos los partidos del día
        """
        logger.info("🏟️  Iniciando análisis predictivo MLB Quant V3...")
        
        try:
            # Obtener partidos programados
            games = self.fetcher.get_todays_games()
            
            if not games:
                logger.warning("⚠️  No hay partidos programados para hoy.")
                return
            
            logger.info(f"📊 {len(games)} partidos encontrados para hoy.")
            
            # Diccionario de estadios
            stadium_map = {
                'NYY': 'Yankee Stadium',
                'BOS': 'Fenway Park',
                'LAD': 'Dodger Stadium',
                'COL': 'Coors Field',
                'TOR': 'Rogers Centre'
            }
            
            all_reports = []
            
            for game in games:
                try:
                    home_abbr = game['home_abbr']
                    park_name = stadium_map.get(home_abbr, 'Unknown Stadium')
                    
                    logger.info(f"Analizando: {game['away_team']} @ {game['home_team']} ({park_name})")
                    
                    # Análisis completo del partido
                    analysis = self.engine.analyze_game(
                        game['home_team'],
                        game['away_team'],
                        park_name
                    )
                    
                    json_report = self.engine.generate_json_report(analysis)
                    all_reports.append(json.loads(json_report))
                    
                    logger.info(f"✅ Análisis completado: {game['away_team']} @ {game['home_team']}")
                    
                except Exception as e:
                    logger.error(f"❌ Error analizando {game['home_team']}: {e}")
                    continue
            
            # Guardar reporte consolidado
            if all_reports:
                self._save_report(all_reports)
                logger.info(f"📁 {len(all_reports)} reportes generados y guardados.")
                return all_reports
            
        except Exception as e:
            logger.error(f"❌ Error en pipeline: {e}")
            return []
    
    def _save_report(self, reports):
        """
        Guarda reporte en archivo JSON
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'reports/mlb_analysis_{timestamp}.json'
        
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'total_games': len(reports),
                'games_analysis': reports
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Reporte guardado en {filename}")

if __name__ == '__main__':
    pipeline = ProductionPipeline()
    reports = pipeline.run_daily_analysis()
    
    if reports:
        # Mostrar resumen de mejor oportunidad por partido
        for report in reports:
            logger.info(f"\n🎯 {report['matchup']}")
            top_option = report['opciones_clasificadas'][0]['opcion_clasificada']
            logger.info(f"   Mejor opción: {top_option['mercado_mlb']}")
            logger.info(f"   Probabilidad: {top_option['probabilidad_matematica_estimada']}")
            logger.info(f"   Confianza: {top_option['score_de_confianza_modelo']}")
