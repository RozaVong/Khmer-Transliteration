from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class FeedbackBase(BaseModel):
    """Base feedback model"""
    prediction_id: str = Field(..., description="ID of the prediction")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=500, description="Optional comment")
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class FeedbackCreate(FeedbackBase):
    """Feedback creation model"""
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None

class FeedbackInDB(FeedbackBase):
    """Feedback model for database"""
    id: int
    user_ip: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True