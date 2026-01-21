import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Security utilities for the application"""
    
    @staticmethod
    def hash_input(text: str) -> str:
        """Hash input text for logging"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID"""
        return f"req_{secrets.token_hex(8)}"
    
    @staticmethod
    def sanitize_user_input(text: str, max_length: int = 500) -> str:
        """Sanitize user input to prevent injection attacks"""
        import html
        # Escape HTML characters
        sanitized = html.escape(text)
        # Remove excessive whitespace
        sanitized = ' '.join(sanitized.split())
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        return sanitized

# Global security instance
security = SecurityManager()