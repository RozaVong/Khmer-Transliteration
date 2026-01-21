import json
import time
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class HelperFunctions:
    """Various helper functions for the application"""
    
    @staticmethod
    def format_khmer_text(text: str) -> str:
        """Format Khmer text for better display"""
        if not text:
            return text
        return text
    
    @staticmethod
    def calculate_confidence_color(confidence: float) -> str:
        """Get color based on confidence score"""
        if confidence >= 80:
            return "#10b981"  # Green
        elif confidence >= 60:
            return "#f59e0b"  # Yellow
        else:
            return "#ef4444"  # Red
    
    @staticmethod
    def save_temporary_data(data: dict, prefix: str = "temp") -> str:
        """Save temporary data to file (for debugging)"""
        try:
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = temp_dir / f"{prefix}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Temporary data saved: {filename}")
            return str(filename)
        except Exception as e:
            logger.error(f"Failed to save temporary data: {str(e)}")
            return ""
    
    @staticmethod
    def format_time_ago(timestamp: datetime) -> str:
        """Format time ago from timestamp"""
        now = datetime.utcnow()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "just now"

# Global helper instance
helpers = HelperFunctions()