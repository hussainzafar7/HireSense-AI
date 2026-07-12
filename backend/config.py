import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "hiresense-dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hiresense-jwt-dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///hiresense.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
