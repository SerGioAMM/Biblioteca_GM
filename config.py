from decouple import config
from datetime import timedelta


class Config():
    SECRET_KEY = config('SECRET_KEY')
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=3)  # Timeout de 3 minutos (para demostración)


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    'development': DevelopmentConfig
}