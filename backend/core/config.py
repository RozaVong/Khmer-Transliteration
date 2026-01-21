import os
from pathlib import Path
from typing import List

class Settings:
    # Base
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Khmer Transliteration API")
    VERSION = os.getenv("VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    MODEL_DIR = BASE_DIR / "model"
    LOGS_DIR = BASE_DIR / "backend" / "logs"
    
    # Ensure directories exist
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Database (Neon PostgreSQL)
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    
    # API
    API_V1_STR = os.getenv("API_V1_STR", "/api/v1")
    
    # CORS - Parse list from environment
    cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:8000","http://localhost:8001","http://localhost"]')
    try:
        CORS_ORIGINS = eval(cors_origins_str) if cors_origins_str else []
    except:
        CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost"]
    
    # Model paths
    MODEL_PATH = MODEL_DIR / "khmer_Glish.keras"
    PICKLE_PATH = MODEL_DIR / "khmer_Glish.pkl"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "a3f4b9e7c1d2f5e6a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2")
    
    # Server port
    PORT = int(os.getenv("PORT", 8001))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    def __init__(self):
        """Initialize settings and validate paths"""
        print(f"📁 BASE_DIR: {self.BASE_DIR}")
        print(f"📁 MODEL_DIR: {self.MODEL_DIR}")
        print(f"📁 MODEL_PATH exists: {self.MODEL_PATH.exists()}")
        print(f"📁 PICKLE_PATH exists: {self.PICKLE_PATH.exists()}")
        
        # Check model files
        if not self.MODEL_PATH.exists():
            print(f"⚠️ WARNING: Model file not found at {self.MODEL_PATH}")
        if not self.PICKLE_PATH.exists():
            print(f"⚠️ WARNING: Pickle file not found at {self.PICKLE_PATH}")

# Global settings instance
settings = Settings()