import re
import logging

logger = logging.getLogger(__name__)

class DataPreprocessor:
    @staticmethod
    def clean_input(text: str, is_khmer: bool = False) -> str:
        """
        Clean input text for processing
        """
        text = text.lower().strip()
        
        if not is_khmer:
            # For English: keep only letters and spaces
            text = re.sub(r'[^a-z\s]', '', text)
        else:
            # For Khmer: keep Khmer characters and spaces
            text = re.sub(r'[^\u1780-\u17FF\s]', '', text)
        
        return text
    
    @staticmethod
    def split_into_words(text: str):
        """
        Split text into individual words
        """
        return [word for word in text.split() if word]
    
    @staticmethod
    def validate_input(text: str, max_length: int = 100):
        """
        Validate input text
        Returns: (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Input cannot be empty"
        
        if len(text) > max_length:
            return False, f"Input too long. Maximum {max_length} characters allowed."
        
        # Check if input contains at least some English letters
        if not re.search(r'[a-zA-Z]', text):
            return False, "Input should contain English characters"
        
        return True, ""