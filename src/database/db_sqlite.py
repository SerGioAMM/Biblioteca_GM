from decouple import config
from src.utils.logger import logger
import traceback

# pip install sqlitecloud
def conexion_BD():
    try:
        if config('ENV', default="Local") == "Produccion":
            # Open the connection to SQLite Cloud
            import sqlitecloud
            return sqlitecloud.connect(config('PATO'))
        else:
            import sqlite3
            import os
            DIR = os.path.dirname(os.path.abspath(__file__))
            RUTA_RELATIVA = config('DB_LOCAL')
            RUTA_DB = os.path.join(DIR, RUTA_RELATIVA)
            return (sqlite3.connect(RUTA_DB))
    except Exception as ex:
        logger.add_to_log("error", str(ex))
        logger.add_to_log("error", traceback.format_exc())
