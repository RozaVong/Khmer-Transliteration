from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from backend.services.translation import translation_service
from backend.services.monitoring import monitoring_service
from backend.models.prediction import Prediction
from backend.utils.data_preprocessing import DataPreprocessor
from backend.core.config import settings
from backend.database.connection import Database

logger = logging.getLogger(__name__)
router = APIRouter()
preprocessor = DataPreprocessor()

# =============== REQUEST/RESPONSE MODELS ===============

class TranslationRequest(BaseModel):
    text: str = Field(..., example="nh", description="English text to translate to Khmer")

    class Config:
        schema_extra = {
            "example": {
                "text": "nh"
            }
        }

class TranslationResponse(BaseModel):
    input_text: str = Field(..., example="nh")
    translation: str = Field(..., example="ខ្ញុំ")
    average_confidence: float = Field(..., example=80.85)
    word_count: int = Field(..., example=1)
    prediction_id: Optional[str] = Field(None, example="8ebdf006-57cd-468c-8ba7-86876e713147")

    class Config:
        schema_extra = {
            "example": {
                "input_text": "nh",
                "translation": "ខ្ញុំ",
                "average_confidence": 80.85,
                "word_count": 1,
                "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147"
            }
        }

class FeedbackRequest(BaseModel):
    prediction_id: str = Field(..., example="8ebdf006-57cd-468c-8ba7-86876e713147")
    rating: int = Field(..., example=5, ge=1, le=5)
    comment: Optional[str] = Field(None, example="Great translation!")

    class Config:
        schema_extra = {
            "example": {
                "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                "rating": 5,
                "comment": "Great translation!"
            }
        }

class FeedbackResponse(BaseModel):
    message: str = Field(..., example="Feedback submitted successfully")
    feedback_id: int = Field(..., example=1)

    class Config:
        schema_extra = {
            "example": {
                "message": "Feedback submitted successfully",
                "feedback_id": 1
            }
        }

class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    model_loaded: bool = Field(..., example=True)
    database_connected: bool = Field(..., example=True)
    version: str = Field(..., example="1.0.0")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "database_connected": True,
                "version": "1.0.0"
            }
        }

class MetricsResponse(BaseModel):
    status: str = Field(..., example="success")
    metrics: Dict[str, Any] = Field(
        ...,
        example={
            "total_predictions": 150,
            "total_errors": 5,
            "total_feedback": 25,
            "database_predictions": 150,
            "database_avg_confidence": 78.5,
            "api_version": "1.0.0"
        }
    )
    timestamp: str = Field(..., example="2024-01-20T10:22:16Z")
    
    @validator('timestamp', pre=True)
    def convert_timestamp(cls, v):
        """Convert datetime to ISO string"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "metrics": {
                    "total_predictions": 150,
                    "total_errors": 5,
                    "total_feedback": 25,
                    "database_predictions": 150,
                    "database_avg_confidence": 78.5,
                    "api_version": "1.0.0"
                },
                "timestamp": "2024-01-20T10:22:16Z"
            }
        }

class PredictionHistory(BaseModel):
    id: str = Field(..., example="8ebdf006-57cd-468c-8ba7-86876e713147")
    input_text: str = Field(..., example="nh")
    output_text: str = Field(..., example="ខ្ញុំ")
    confidence: float = Field(..., example=80.85)
    created_at: str = Field(..., example="2024-01-20T10:22:16Z")
    
    @validator('created_at', pre=True)
    def convert_datetime_to_str(cls, v):
        """Convert datetime objects to ISO format string"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                "input_text": "nh",
                "output_text": "ខ្ញុំ",
                "confidence": 80.85,
                "created_at": "2024-01-20T10:22:16Z"
            }
        }

class FeedbackItem(BaseModel):
    id: int = Field(..., example=1)
    prediction_id: str = Field(..., example="8ebdf006-57cd-468c-8ba7-86876e713147")
    rating: int = Field(..., example=5)
    comment: Optional[str] = Field(None, example="Great translation!")
    user_ip: Optional[str] = Field(None, example="127.0.0.1")
    created_at: str = Field(..., example="2024-01-20T10:25:00Z")
    
    @validator('created_at', pre=True)
    def convert_datetime_to_str(cls, v):
        """Convert datetime objects to ISO format string"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                "rating": 5,
                "comment": "Great translation!",
                "user_ip": "127.0.0.1",
                "created_at": "2024-01-20T10:25:00Z"
            }
        }

class PredictionDetail(BaseModel):
    id: str = Field(..., example="8ebdf006-57cd-468c-8ba7-86876e713147")
    input_text: str = Field(..., example="nh")
    output_text: str = Field(..., example="ខ្ញុំ")
    confidence: float = Field(..., example=80.85)
    user_ip: str = Field(..., example="127.0.0.1")
    user_agent: str = Field(..., example="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    created_at: str = Field(..., example="2024-01-20T10:22:16Z")
    updated_at: str = Field(..., example="2024-01-20T10:22:16Z")
    feedback: Optional[List[FeedbackItem]] = Field(default_factory=list)
    
    @validator('created_at', 'updated_at', pre=True)
    def convert_datetime_fields(cls, v):
        """Convert datetime objects to ISO format string"""
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    class Config:
        schema_extra = {
            "example": {
                "id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                "input_text": "nh",
                "output_text": "ខ្ញុំ",
                "confidence": 80.85,
                "user_ip": "127.0.0.1",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "created_at": "2024-01-20T10:22:16Z",
                "updated_at": "2024-01-20T10:22:16Z",
                "feedback": [
                    {
                        "id": 1,
                        "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                        "rating": 5,
                        "comment": "Great translation!",
                        "user_ip": "127.0.0.1",
                        "created_at": "2024-01-20T10:25:00Z"
                    }
                ]
            }
        }

class PredictionDetailResponse(BaseModel):
    prediction: PredictionDetail

    class Config:
        schema_extra = {
            "example": {
                "prediction": {
                    "id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                    "input_text": "nh",
                    "output_text": "ខ្ញុំ",
                    "confidence": 80.85,
                    "user_ip": "127.0.0.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "created_at": "2024-01-20T10:22:16Z",
                    "updated_at": "2024-01-20T10:22:16Z",
                    "feedback": [
                        {
                            "id": 1,
                            "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                            "rating": 5,
                            "comment": "Great translation!",
                            "user_ip": "127.0.0.1",
                            "created_at": "2024-01-20T10:25:00Z"
                        }
                    ]
                }
            }
        }

# =============== API ENDPOINTS ===============

@router.post(
    "/translate",
    response_model=TranslationResponse,
    responses={
        200: {
            "description": "Translation completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "input_text": "nh",
                        "translation": "ខ្ញុំ",
                        "average_confidence": 80.85,
                        "word_count": 1,
                        "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Input cannot be empty"
                    }
                }
            }
        },
        500: {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Translation failed: Model not loaded"
                    }
                }
            }
        }
    }
)
async def translate_text(request: Request, data: TranslationRequest):
    """
    Translate English text to Khmer transliteration.
    
    **Example Request:**
    ```json
    {
        "text": "nh"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "input_text": "nh",
        "translation": "ខ្ញុំ",
        "average_confidence": 80.85,
        "word_count": 1,
        "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147"
    }
    ```
    """
    try:
        logger.info(f"🔤 Translation request: '{data.text}'")
        
        if not data.text or not data.text.strip():
            raise HTTPException(status_code=400, detail="Input cannot be empty")
        
        if len(data.text) > 100:
            raise HTTPException(status_code=400, detail="Input too long. Max 100 characters.")
        
        result = translation_service.translate_text(data.text)
        logger.info(f"✅ Translation complete: '{result['translation']}'")
        
        prediction = Prediction(
            input_text=data.text,
            output_text=result['translation'],
            confidence=result['average_confidence']
        )
        
        prediction.user_ip = request.client.host if request.client else None
        prediction.user_agent = request.headers.get('user-agent')
        
        prediction_id = translation_service.save_prediction(prediction)
        
        monitoring_service.log_prediction({
            'prediction_id': prediction_id,
            'input': data.text,
            'output': result['translation'],
            'confidence': result['average_confidence'],
            'user_ip': prediction.user_ip
        })
        
        return TranslationResponse(
            input_text=data.text,
            translation=result['translation'],
            average_confidence=result['average_confidence'],
            word_count=result['word_count'],
            prediction_id=prediction_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Translation error: {str(e)}")
        
        monitoring_service.log_error({
            'error': str(e),
            'input': data.text,
            'endpoint': '/translate'
        })
        
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    responses={
        200: {
            "description": "Feedback submitted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Feedback submitted successfully",
                        "feedback_id": 1
                    }
                }
            }
        },
        400: {
            "description": "Invalid rating",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Rating must be between 1 and 5"
                    }
                }
            }
        },
        500: {
            "description": "Server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to save feedback"
                    }
                }
            }
        }
    }
)
async def submit_feedback(data: FeedbackRequest):
    """
    Submit feedback for a prediction.
    
    **Example Request:**
    ```json
    {
        "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147",
        "rating": 5,
        "comment": "Great translation!"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "message": "Feedback submitted successfully",
        "feedback_id": 1
    }
    ```
    """
    try:
        if not 1 <= data.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        query = """
        INSERT INTO feedback (prediction_id, rating, comment, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        
        result = Database.execute_query(
            query,
            (data.prediction_id, data.rating, data.comment, datetime.utcnow()),
            fetch_one=True
        )
        
        if result:
            monitoring_service.log_user_feedback({
                'prediction_id': data.prediction_id,
                'rating': data.rating,
                'comment': data.comment,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"⭐ Feedback submitted for {data.prediction_id}: {data.rating} stars")
            
            return FeedbackResponse(
                message="Feedback submitted successfully",
                feedback_id=result['id']
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to save feedback")
        
    except Exception as e:
        logger.error(f"Feedback submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "System health check",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "model_loaded": True,
                        "database_connected": True,
                        "version": "1.0.0"
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Health check endpoint.
    
    **Example Response:**
    ```json
    {
        "status": "healthy",
        "model_loaded": True,
        "database_connected": True,
        "version": "1.0.0"
    }
    ```
    """
    try:
        from backend.utils.model_loader import model_loader
        model_loaded = False
        
        try:
            # Try to initialize if not already initialized
            if not model_loader._initialized:
                model_loader.initialize()
            model_loaded = True
        except Exception as e:
            logger.error(f"Model initialization failed in health check: {e}")
            model_loaded = False
            
        database_connected = Database.check_connection()
        
        if model_loaded and database_connected:
            status = "healthy"
        elif model_loaded or database_connected:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return HealthResponse(
            status=status,
            model_loaded=model_loaded,
            database_connected=database_connected,
            version=settings.VERSION
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            database_connected=False,
            version=settings.VERSION
        )

@router.get(
    "/metrics",
    response_model=MetricsResponse,
    responses={
        200: {
            "description": "System metrics",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "metrics": {
                            "total_predictions": 150,
                            "total_errors": 5,
                            "total_feedback": 25,
                            "database_predictions": 150,
                            "database_avg_confidence": 78.5,
                            "api_version": "1.0.0"
                        },
                        "timestamp": "2024-01-20T10:22:16Z"
                    }
                }
            }
        }
    }
)
async def get_metrics():
    """
    Get system metrics.
    
    **Example Response:**
    ```json
    {
        "status": "success",
        "metrics": {
            "total_predictions": 150,
            "total_errors": 5,
            "total_feedback": 25,
            "database_predictions": 150,
            "database_avg_confidence": 78.5,
            "api_version": "1.0.0"
        },
        "timestamp": "2024-01-20T10:22:16Z"
    }
    ```
    """
    try:
        total_predictions = 0
        avg_confidence = 0
        
        try:
            result = Database.execute_query(
                "SELECT COUNT(*) as count, AVG(confidence) as avg FROM predictions",
                fetch_one=True
            )
            if result:
                total_predictions = result['count'] or 0
                avg_confidence = round(float(result['avg'] or 0), 2)
        except Exception as db_error:
            logger.warning(f"Could not get database metrics: {db_error}")
        
        metrics = monitoring_service.get_metrics()
        metrics.update({
            'database_predictions': total_predictions,
            'database_avg_confidence': avg_confidence,
            'api_version': settings.VERSION
        })
        
        return MetricsResponse(
            status="success",
            metrics=metrics,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return MetricsResponse(
            status="error",
            metrics={"error": str(e)},
            timestamp=datetime.utcnow().isoformat()
        )

@router.get(
    "/predictions",
    response_model=List[PredictionHistory],
    responses={
        200: {
            "description": "List of recent predictions",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                            "input_text": "nh",
                            "output_text": "ខ្ញុំ",
                            "confidence": 80.85,
                            "created_at": "2024-01-20T10:22:16Z"
                        },
                        {
                            "id": "99450e5a-70ca-49d3-8f58-4432a6588e8f",
                            "input_text": "hello",
                            "output_text": "ហេឡូ",
                            "confidence": 85.5,
                            "created_at": "2024-01-20T10:20:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def get_predictions(limit: int = 10, offset: int = 0):
    """
    Get recent predictions from database.
    
    **Query Parameters:**
    - `limit`: Number of predictions to return (default: 10)
    - `offset`: Number of predictions to skip (default: 0)
    
    **Example Response:**
    ```json
    [
        {
            "id": "8ebdf006-57cd-468c-8ba7-86876e713147",
            "input_text": "nh",
            "output_text": "ខ្ញុំ",
            "confidence": 80.85,
            "created_at": "2024-01-20T10:22:16Z"
        }
    ]
    ```
    """
    try:
        query = """
        SELECT id, input_text, output_text, confidence, created_at
        FROM predictions 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        
        results = Database.execute_query(query, (limit, offset), fetch_all=True)
        
        formatted_predictions = []
        for pred in results:
            formatted_predictions.append(PredictionHistory(
                id=pred['id'],
                input_text=pred['input_text'],
                output_text=pred['output_text'],
                confidence=float(pred['confidence']),
                created_at=pred['created_at']
            ))
        
        return formatted_predictions
        
    except Exception as e:
        logger.error(f"Failed to get predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get predictions: {str(e)}")

@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionDetailResponse,
    responses={
        200: {
            "description": "Prediction details with feedback",
            "content": {
                "application/json": {
                    "example": {
                        "prediction": {
                            "id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                            "input_text": "nh",
                            "output_text": "ខ្ញុំ",
                            "confidence": 80.85,
                            "user_ip": "127.0.0.1",
                            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                            "created_at": "2024-01-20T10:22:16Z",
                            "updated_at": "2024-01-20T10:22:16Z",
                            "feedback": [
                                {
                                    "id": 1,
                                    "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                                    "rating": 5,
                                    "comment": "Great translation!",
                                    "user_ip": "127.0.0.1",
                                    "created_at": "2024-01-20T10:25:00Z"
                                }
                            ]
                        }
                    }
                }
            }
        },
        404: {
            "description": "Prediction not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Prediction not found"
                    }
                }
            }
        }
    }
)
async def get_prediction(prediction_id: str):
    """
    Get a specific prediction by ID with associated feedback.
    
    **Path Parameter:**
    - `prediction_id`: The UUID of the prediction
    
    **Example Response:**
    ```json
    {
        "prediction": {
            "id": "8ebdf006-57cd-468c-8ba7-86876e713147",
            "input_text": "nh",
            "output_text": "ខ្ញុំ",
            "confidence": 80.85,
            "user_ip": "127.0.0.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "created_at": "2024-01-20T10:22:16Z",
            "updated_at": "2024-01-20T10:22:16Z",
            "feedback": [
                {
                    "id": 1,
                    "prediction_id": "8ebdf006-57cd-468c-8ba7-86876e713147",
                    "rating": 5,
                    "comment": "Great translation!",
                    "user_ip": "127.0.0.1",
                    "created_at": "2024-01-20T10:25:00Z"
                }
            ]
        }
    }
    ```
    """
    try:
        query = """
        SELECT p.*, 
               (SELECT json_agg(f) FROM feedback f WHERE f.prediction_id = p.id) as feedback
        FROM predictions p
        WHERE p.id = %s
        """
        
        result = Database.execute_query(query, (prediction_id,), fetch_one=True)
        
        if not result:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Handle None feedback
        if result.get('feedback') is None:
            result['feedback'] = []
        
        return PredictionDetailResponse(prediction=PredictionDetail(**result))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get prediction: {str(e)}")