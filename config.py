from decouple import config
from datetime import timedelta


class Config():
    SECRET_KEY = config('SECRET_KEY')
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=3)  # Timeout de 3 minutos (para demostración) #! Cambiar a timedelta(minutes=15) para 15 minutos


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    'development': DevelopmentConfig
}