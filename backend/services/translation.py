import logging
from typing import Dict, Any
from backend.utils.model_loader import model_loader
from backend.utils.data_preprocessing import DataPreprocessor
from backend.models.prediction import Prediction
from backend.database.connection import Database

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        # Initialize model loader - but don't load model here
        # Let it load lazily when first prediction is made
        logger.info("Translation service initialized - model will load on first use")
    
    def translate_single_word(self, word: str):
        """
        Translate a single word EXACTLY like Colab
        Returns: (translation, confidence)
        """
        try:
            return model_loader.predict_khmer_with_confidence(word)
        except Exception as e:
            logger.error(f"Error translating word '{word}': {str(e)}")
            return f"[{word}]", 0.0
    
    def translate_text(self, text: str) -> Dict[str, Any]:
        """
        Translate full text containing multiple words EXACTLY like Colab
        """
        logger.info(f"Translating text: '{text}'")
        
        # Split into words
        words = text.split()
        
        if not words:
            return {
                'input_text': text,
                'translation': '',
                'word_translations': [],
                'average_confidence': 0.0,
                'word_count': 0
            }
        
        results = []
        total_confidence = 0
        
        # Translate each word
        for word in words:
            translation, confidence = self.translate_single_word(word)
            logger.info(f"  '{word}' -> '{translation}' ({confidence}%)")
            
            results.append({
                'input': word,
                'translation': translation,
                'confidence': confidence
            })
            total_confidence += confidence
        
        # Join translations WITHOUT spaces (like Colab)
        full_translation = ''.join([r['translation'] for r in results])
        avg_confidence = total_confidence / len(results) if results else 0
        
        logger.info(f"Full translation: '{full_translation}' (avg: {avg_confidence:.2f}%)")
        
        return {
            'input_text': text,
            'translation': full_translation,
            'word_translations': results,
            'average_confidence': round(avg_confidence, 2),
            'word_count': len(words)
        }
    
    def save_prediction(self, prediction: Prediction) -> str:
        """
        Save prediction to database
        """
        try:
            query = """
            INSERT INTO predictions (id, input_text, output_text, confidence, user_ip, user_agent, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            result = Database.execute_query(
                query,
                (
                    prediction.id,
                    prediction.input_text,
                    prediction.output_text,
                    float(prediction.confidence),
                    prediction.user_ip,
                    prediction.user_agent,
                    prediction.timestamp
                ),
                fetch_one=True
            )
            
            if result:
                logger.info(f"Prediction saved: {prediction.id}")
                return prediction.id
            else:
                logger.warning("Failed to save prediction")
                return prediction.id

        except Exception as e:
            logger.error(f"Failed to save prediction to database: {str(e)}")
            # Return ID even if database save fails
            return prediction.id
    
    def get_recent_predictions(self, limit: int = 10):
        """
        Get recent predictions from database
        """
        try:
            query = """
            SELECT id, input_text, output_text, confidence, user_ip, created_at
            FROM predictions 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            results = Database.execute_query(query, (limit,), fetch_all=True)
            return results or []
            
        except Exception as e:
            logger.error(f"Failed to get predictions: {str(e)}")
            return []

# Singleton instance
translation_service = TranslationService()