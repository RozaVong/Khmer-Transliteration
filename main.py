# =============== CRITICAL: TENSORFLOW SETUP ===============
import os
import sys

# Set environment variables BEFORE importing TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all TensorFlow logs
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'false'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

print("🚀 TensorFlow environment configured")

# =============== PATH SETUP ===============
# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"📁 Current directory: {current_dir}")

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Try to import backend modules
try:
    print("🔍 Attempting to import from backend module...")
    
    # Add backend directory to path
    backend_dir = os.path.join(BASE_DIR, "backend")
    sys.path.insert(0, backend_dir)
    
    # Import backend modules
    from backend.core.config import settings
    from backend.api.v1.routes import router as api_router
    from backend.utils.model_loader import model_loader
    from backend.database.connection import Database
    from backend.database.migrations import run_initial_migration
    
    print("✅ Successfully imported backend modules")
    IMPORT_SUCCESS = True
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    
    # Create dummy objects
    class DummySettings:
        PROJECT_NAME = "Khmer Transliteration API"
        VERSION = "1.0.0"
        DEBUG = True
        LOG_LEVEL = "INFO"
        API_V1_STR = "/api/v1"
        CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost"]
        PORT = 8001
        DATABASE_URL = ""
        SECRET_KEY = "dummy"
        RATE_LIMIT_PER_MINUTE = 60
        HOST = "0.0.0.0"
        
    settings = DummySettings()
    api_router = None
    model_loader = type('obj', (object,), {'_initialized': False, 'initialize': lambda self: None, 'predict': lambda self, x: ("", 0.0)})()
    Database = type('obj', (object,), {'check_connection': classmethod(lambda cls: False), 'execute_query': classmethod(lambda cls, *args, **kwargs: None)})()
    run_initial_migration = lambda: False
    IMPORT_SUCCESS = False

# =============== NORMAL IMPORTS ===============
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime

# Logging setup
LOG_DIR = os.path.join(BASE_DIR, "backend", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
log_level = getattr(settings, 'LOG_LEVEL', 'INFO') if IMPORT_SUCCESS else 'INFO'

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8")
    ],
)

logger = logging.getLogger(__name__)

# =============== RESPONSE MODELS ===============

class TestResult(BaseModel):
    input: str = Field(..., example="nhom")
    output: str = Field(..., example="ញ៉ុម")
    confidence: float = Field(..., example=79.08)

    class Config:
        schema_extra = {
            "example": {
                "input": "nhom",
                "output": "ញ៉ុម",
                "confidence": 79.08
            }
        }

class ServerInfo(BaseModel):
    port: int = Field(..., example=8001)
    host: str = Field(..., example="0.0.0.0")
    version: str = Field(..., example="1.0.0")
    project_name: str = Field(..., example="Khmer Transliteration")

    class Config:
        schema_extra = {
            "example": {
                "port": 8001,
                "host": "0.0.0.0",
                "version": "1.0.0",
                "project_name": "Khmer Transliteration"
            }
        }

class TestResponse(BaseModel):
    status: str = Field(..., example="ok")
    model: str = Field(..., example="loaded")
    database: bool = Field(..., example=True)
    results: List[TestResult]
    timestamp: str = Field(..., example="2026-01-20T14:16:46Z")
    server_info: ServerInfo
    
    @validator('timestamp', pre=True)
    def convert_timestamp(cls, v):
        """Convert datetime to ISO string"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "model": "loaded",
                "database": True,
                "results": [
                    {
                        "input": "nhom",
                        "output": "ញ៉ុម",
                        "confidence": 79.08
                    },
                    {
                        "input": "tv",
                        "output": "ទៅ",
                        "confidence": 80.58
                    },
                    {
                        "input": "sala",
                        "output": "សាលា",
                        "confidence": 76.3
                    }
                ],
                "timestamp": "2026-01-20T14:16:46Z",
                "server_info": {
                    "port": 8001,
                    "host": "0.0.0.0",
                    "version": "1.0.0",
                    "project_name": "Khmer Transliteration"
                }
            }
        }

# FastAPI app
app = FastAPI(
    title=getattr(settings, 'PROJECT_NAME', 'Khmer Transliteration API'),
    version=getattr(settings, 'VERSION', '1.0.0'),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    description="Khmer Transliteration API - Translate English text to Khmer",
)

# CORS
if hasattr(settings, 'CORS_ORIGINS'):
    origins = settings.CORS_ORIGINS
else:
    origins = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8001", "http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static / Frontend
frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    logger.info(f"Static files mounted at /static from {frontend_dir}")

# API routes
if IMPORT_SUCCESS and api_router is not None:
    app.include_router(api_router, prefix=getattr(settings, 'API_V1_STR', '/api/v1'))
    logger.info("✅ API router included")

# =============== DEFAULT ENDPOINTS ===============

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🇰🇭 Khmer Transliteration API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                max-width: 800px;
                margin: 0 auto;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 { color: #ffd700; font-size: 2.5em; }
            .status { 
                padding: 15px; 
                background: rgba(0,255,0,0.2); 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 5px solid #00ff00;
            }
            .endpoint {
                background: rgba(255,255,255,0.1);
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .method {
                font-weight: bold;
                color: #ffd700;
            }
            .path {
                font-family: monospace;
                background: rgba(0,0,0,0.2);
                padding: 5px 10px;
                border-radius: 5px;
            }
            a { color: #ffd700; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🇰🇭 Khmer Transliteration API</h1>
            <div class="status">✅ Backend is running on port 8001</div>
            
            <h2>📚 API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/v1/translate</span>
                <p>Translate English text to Khmer</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="path">/api/v1/feedback</span>
                <p>Submit feedback for translations</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="path">/api/v1/health</span>
                <p>Check system health</p>
            </div>
            
            <h2>🔗 Quick Links</h2>
            <ul>
                <li><a href="/docs" target="_blank">📖 Interactive API Documentation (Swagger)</a></li>
                <li><a href="/redoc" target="_blank">📚 Alternative Documentation (ReDoc)</a></li>
                <li><a href="/test">🧪 Test Endpoint</a></li>
                <li><a href="/api/v1/health">❤️‍🩹 Health Check</a></li>
            </ul>
        </div>
    </body>
    </html>
    """)

@app.get("/test", response_model=TestResponse)
async def test_endpoint():
    try:
        test_words = ["nhom", "tv", "sala"]
        results = []

        for word in test_words:
            try:
                if hasattr(model_loader, 'predict'):
                    text, confidence = model_loader.predict(word)
                    results.append(TestResult(
                        input=word,
                        output=text,
                        confidence=confidence
                    ))
                else:
                    results.append(TestResult(
                        input=word,
                        output="Model not loaded",
                        confidence=0.0
                    ))
            except Exception as e:
                results.append(TestResult(
                    input=word,
                    output=f"Error: {str(e)[:50]}",
                    confidence=0.0
                ))

        return TestResponse(
            status="ok",
            model="loaded" if hasattr(model_loader, '_initialized') and model_loader._initialized else "not loaded",
            database=Database.check_connection() if hasattr(Database, 'check_connection') else False,
            results=results,
            timestamp=datetime.utcnow().isoformat() + "Z",
            server_info=ServerInfo(
                port=getattr(settings, 'PORT', 8001),
                host="0.0.0.0",
                version=getattr(settings, 'VERSION', '1.0.0'),
                project_name=getattr(settings, 'PROJECT_NAME', 'Khmer Transliteration')
            )
        )

    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        return {"status": "error", "message": str(e)[:100]}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint not found",
            "request_path": request.url.path
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Khmer Transliteration API")
    
    if IMPORT_SUCCESS:
        try:
            # Initialize model
            if hasattr(model_loader, 'initialize'):
                try:
                    model_loader.initialize()
                    logger.info("✅ Model initialized successfully")
                except Exception as model_error:
                    logger.error(f"❌ Model initialization failed: {model_error}")
            
            # Initialize database
            try:
                if hasattr(Database, 'setup_tables'):
                    Database.setup_tables()
                    logger.info("✅ Database tables setup")
                
                if hasattr(Database, 'check_connection'):
                    if Database.check_connection():
                        logger.info("✅ Database connected successfully")
                    else:
                        logger.warning("⚠️ Database connection failed")
            except Exception as db_error:
                logger.error(f"❌ Database error: {db_error}")
                
        except Exception as e:
            logger.error(f"❌ Startup error: {e}")
    
    port = getattr(settings, 'PORT', 8001)
    logger.info(f"🌐 Server running on: http://localhost:{port}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Shutting down Khmer Transliteration API")

# Main entry point
if __name__ == "__main__":
    port = getattr(settings, 'PORT', 8001)
    
    logger.info(f"🌐 Starting server on http://localhost:{port}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        access_log=True,
        log_level="info"
    )