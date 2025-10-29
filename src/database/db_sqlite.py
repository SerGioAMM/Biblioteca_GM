from decouple import config
from src.utils.logger import logger
import traceback

# pip install sqlitecloud
def conexion_BD():
    try:
        if config('ENV', default="Local") == "Cloud":
            # Open the connection to SQLite Cloud
            import sqlitecloud
            return sqlitecloud.connect(config('SQLITE_CLOUD_CONN'))
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
        raise RuntimeError("No se pudo conectar a la base de datos")

def dict_factory(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]