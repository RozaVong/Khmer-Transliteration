import os
import pickle
import re
import numpy as np
import logging
from backend.core.config import settings

# Set Keras backend to TensorFlow before importing keras
os.environ['KERAS_BACKEND'] = 'tensorflow'

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self):
        """Initialize model and tokenizers - Using Keras 3.x"""
        if self._initialized:
            return
        
        logger.info("🧠 Initializing Model Loader")
        
        # Check if files exist
        if not settings.MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {settings.MODEL_PATH}")
        if not settings.PICKLE_PATH.exists():
            raise FileNotFoundError(f"Pickle file not found: {settings.PICKLE_PATH}")
        
        logger.info(f"✅ Model file: {settings.MODEL_PATH}")
        logger.info(f"✅ Pickle file: {settings.PICKLE_PATH}")
        
        try:
            # Use standalone Keras 3.x for .keras model format
            import keras
            from keras.models import load_model
            logger.info(f"✅ Using Keras {keras.__version__}")
            
            # Load model
            logger.info("📥 Loading model...")
            self.model = load_model(str(settings.MODEL_PATH))
            logger.info("✅ Model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            raise
        
        # Load tokenizers
        logger.info("📥 Loading tokenizers...")
        try:
            with open(str(settings.PICKLE_PATH), 'rb') as f:
                assets = pickle.load(f)
            
            self.eng_tokenizer = assets['eng_tokenizer']
            self.khm_tokenizer = assets['khm_tokenizer']
            self.max_eng_len = assets['max_eng_len']
            self.max_khm_len = assets['max_khm_len']
            
            logger.info(f"✅ English vocab size: {len(self.eng_tokenizer.word_index) + 1}")
            logger.info(f"✅ Khmer vocab size: {len(self.khm_tokenizer.word_index) + 1}")
            logger.info(f"✅ Max English length: {self.max_eng_len}")
            logger.info(f"✅ Max Khmer length: {self.max_khm_len}")
            
        except Exception as e:
            logger.error(f"❌ Tokenizer load error: {e}")
            raise
        
        self._initialized = True
        logger.info("🎉 Model initialization complete!")
    
    def _pad_sequences(self, sequences, maxlen, padding='post'):
        """Pad sequences to the same length - compatible with Keras 3.x"""
        padded = np.zeros((len(sequences), maxlen), dtype=np.int32)
        for i, seq in enumerate(sequences):
            if len(seq) > maxlen:
                if padding == 'post':
                    padded[i] = seq[:maxlen]
                else:
                    padded[i] = seq[-maxlen:]
            else:
                if padding == 'post':
                    padded[i, :len(seq)] = seq
                else:
                    padded[i, -len(seq):] = seq
        return padded
    
    def clean_text(self, text, is_khmer=False):
        """Clean input text"""
        text = text.lower().strip()
        if not is_khmer:
            text = re.sub(r'[^a-z\s]', '', text)
        return text
    
    def predict_khmer_with_confidence(self, eng_input):
        """
        Translate English word to Khmer with confidence
        """
        if not self._initialized:
            self.initialize()
        
        cleaned = self.clean_text(eng_input, is_khmer=False)
        
        if len(cleaned) == 0:
            return "", 0.0

        try:
            # Encode input
            enc_seq = self.eng_tokenizer.texts_to_sequences([cleaned])
            
            if not enc_seq or len(enc_seq[0]) == 0:
                # Try character by character
                chars = list(cleaned)
                enc_seq = []
                for char in chars:
                    if char in self.eng_tokenizer.word_index:
                        enc_seq.append(self.eng_tokenizer.word_index[char])
                    elif char == ' ':
                        enc_seq.append(1)
                    else:
                        enc_seq.append(0)
                enc_seq = [enc_seq]
            
            enc_padded = self._pad_sequences(enc_seq, maxlen=self.max_eng_len, padding='post')
            
            # Get start/end tokens
            start_idx = self.khm_tokenizer.word_index.get('\t')
            end_idx = self.khm_tokenizer.word_index.get('\n')
            
            if start_idx is None or end_idx is None:
                return f"[{eng_input}]", 0.0
            
            # Greedy decoding
            decoder_seq = [start_idx]
            confidences = []

            for t in range(self.max_khm_len + 10):
                dec_padded = self._pad_sequences([decoder_seq], maxlen=self.max_khm_len + 1, padding='post')
                preds = self.model.predict([enc_padded, dec_padded], verbose=0)
                
                time_index = len(decoder_seq) - 1
                if time_index >= preds.shape[1]:
                    break
                
                probs = preds[0, time_index]
                next_token = int(np.argmax(probs))
                confidence = float(probs[next_token])
                
                confidences.append(confidence)
                decoder_seq.append(next_token)
                
                if next_token == end_idx or t == self.max_khm_len + 9:
                    break

            # Decode
            decoded_chars = []
            for idx in decoder_seq[1:]:
                if idx == end_idx:
                    break
                char = self.khm_tokenizer.index_word.get(idx, '')
                decoded_chars.append(char)

            result = ''.join(decoded_chars)
            avg_conf = np.mean(confidences) * 100 if confidences else 0
            
            # If no translation, return fallback
            if not result or result.isspace():
                result = f"[{eng_input}]"
                avg_conf = 0.0
            
            return result, round(avg_conf, 2)
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {str(e)}")
            return f"[{eng_input}]", 0.0
    
    def predict(self, eng_input):
        """Alias for predict_khmer_with_confidence"""
        return self.predict_khmer_with_confidence(eng_input)

# Global instance
model_loader = ModelLoader()