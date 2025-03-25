import os
from sqlalchemy import create_engine
import urllib

class Config:
    SECRET_KEY = "123Tamarindo"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = "123Tamarindo"

class DevelopmentConfig(Config):  
    DEBUG = True
    # Cambiado para incluir ambas bases de datos en una sola
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:sergio@localhost:3306/pizzeria'
    SQLALCHEMY_TRACK_MODIFICATIONS = False